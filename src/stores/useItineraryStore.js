import { create } from "zustand";
import { devtools } from "zustand/middleware";
import {
  fetchUserItinerariesAPI,
  fetchItineraryByIdAPI,
  createItineraryAPI,
  deleteItineraryAPI,
} from "../apis/itineraryService";
import {
  addStopAPI,
  updateStopAPI,
  deleteStopAPI,
  fetchItineraryStopsAPI,
} from "../apis/stopService";

/**
 * Zustand Store for Itinerary Management
 * Handles itinerary data, bookings, highlights, route information, and plan management
 */
const useItineraryStore = create(
  devtools(
    (set, get) => ({
      // ========== State ==========
      itineraryItems: [],
      currentItinerary: null, // Current itinerary metadata { id, title, start_date, end_date, etc }
      includeUserLocation: false, // Whether to include user location as starting point
      isLoading: false,
      error: null,
      activeBooking: null, // Currently booking stop { dayIndex, stopId }
      lastBookedStopId: null, // For highlighting
      routeCache: {}, // Cache routes per day: { dayIndex: routeData }

      // Plan Management State (migrated from PlanContext)
      plan: {
        planId: "default-plan",
        items: [],
        isOptimized: false,
        isOptimizing: false,
        totalDistanceKm: 0,
        estimatedDurationMin: 0,
      },

      // ========== Actions ==========

      /**
       * Initialize/fetch itinerary data from backend
       * @param {Array} data - Itinerary items array
       */
      setItinerary: (data) =>
        set({ itineraryItems: data, isLoading: false, error: null }),

      /**
       * Set loading state
       */
      setLoading: (isLoading) => set({ isLoading }),

      /**
       * Set error state
       */
      setError: (error) => set({ error, isLoading: false }),

      /**
       * Set current itinerary metadata
       */
      setCurrentItinerary: (itinerary) => set({ currentItinerary: itinerary }),

      /**
       * Refresh current itinerary data from backend
       */
      refreshCurrentItinerary: async () => {
        const current = get().currentItinerary;
        if (!current?.id) return;

        set({ isLoading: true });
        try {
          const updated = await fetchItineraryByIdAPI(current.id);
          if (updated) {
            set({
              itineraryItems: updated.days || [],
              currentItinerary: updated,
              isLoading: false,
              error: null,
            });
          }
        } catch (err) {
          set({ error: err.message, isLoading: false });
        }
      },

      /**
       * Toggle whether to include user location as starting point
       */
      toggleUserLocation: () => {
        const current = get().includeUserLocation;
        set({ includeUserLocation: !current });
        // Clear route cache to force recalculation
        set({ routeCache: {} });
      },

      /**
       * Reorder stops within a specific day
       * @param {number} dayIndex - Index of the day
       * @param {Array} newStops - Reordered stops array
       */
      reorderStops: (dayIndex, newStops) => {
        const items = [...get().itineraryItems];
        if (items[dayIndex]) {
          items[dayIndex] = {
            ...items[dayIndex],
            stops: newStops,
          };
          set({ itineraryItems: items });

          // Clear route cache for this day to trigger recalculation
          const routeCache = { ...get().routeCache };
          delete routeCache[dayIndex];
          set({ routeCache });
        }
      },

      /**
       * Reorder entire days
       * @param {Array} newDayOrder - Reordered array of day objects
       */
      reorderDays: (newDayOrder) => {
        set({ itineraryItems: newDayOrder });
        // Clear all route cache
        set({ routeCache: {} });
      },

      /**
       * Book a specific stop
       * @param {number} dayIndex - Index of the day
       * @param {string} stopId - ID of the stop to book
       */
      bookStop: (dayIndex, stopId) => {
        const items = [...get().itineraryItems];
        if (items[dayIndex]) {
          const stopIndex = items[dayIndex].stops.findIndex(
            (s) => s.id === stopId
          );

          if (stopIndex !== -1) {
            items[dayIndex].stops[stopIndex] = {
              ...items[dayIndex].stops[stopIndex],
              isBooked: true,
              bookedAt: new Date().toISOString(),
            };

            set({
              itineraryItems: items,
              lastBookedStopId: stopId,
              activeBooking: null,
            });
          }
        }
      },

      /**
       * Start booking process
       * @param {number} dayIndex - Index of the day
       * @param {string} stopId - ID of the stop
       */
      startBooking: (dayIndex, stopId) => {
        set({ activeBooking: { dayIndex, stopId } });
      },

      /**
       * Cancel booking process
       */
      cancelBooking: () => {
        set({ activeBooking: null });
      },

      /**
       * Update route data for a specific day
       * @param {number} dayIndex - Index of the day
       * @param {Object} routeData - Route data from GraphHopper
       */
      updateRouteData: (dayIndex, routeData) => {
        const routeCache = { ...get().routeCache };
        routeCache[dayIndex] = {
          data: routeData,
          calculatedAt: new Date().toISOString(),
        };
        set({ routeCache });
      },

      /**
       * Get route data for a specific day
       * @param {number} dayIndex - Index of the day
       * @returns {Object|null} Route data or null
       */
      getRouteData: (dayIndex) => {
        return get().routeCache[dayIndex]?.data || null;
      },

      /**
       * Reset all bookings
       */
      resetBookings: () => {
        const items = get().itineraryItems.map((day) => ({
          ...day,
          stops:
            day.stops?.map((stop) => ({
              ...stop,
              isBooked: false,
              bookedAt: undefined,
            })) || [],
        }));
        set({
          itineraryItems: items,
          lastBookedStopId: null,
          activeBooking: null,
        });
      },

      /**
       * Clear highlight from last booked stop
       */
      clearHighlight: () => {
        set({ lastBookedStopId: null });
      },

      /**
       * Add a new stop to a day
       * @param {number} dayIndex - Index of the day
       * @param {Object} newStop - Stop object to add
       */
      addStop: (dayIndex, newStop) => {
        const items = [...get().itineraryItems];
        if (items[dayIndex]) {
          items[dayIndex] = {
            ...items[dayIndex],
            stops: [...(items[dayIndex].stops || []), newStop],
          };
          set({ itineraryItems: items });

          // Clear route cache for this day
          const routeCache = { ...get().routeCache };
          delete routeCache[dayIndex];
          set({ routeCache });
        }
      },

      /**
       * Remove a stop from a day
       * @param {number} dayIndex - Index of the day
       * @param {string} stopId - ID of the stop to remove
       */
      removeStop: (dayIndex, stopId) => {
        const items = [...get().itineraryItems];
        if (!items[dayIndex]) return;

        const stops = [...items[dayIndex].stops];
        const stopIndex = stops.findIndex((s) => s.id === stopId);

        if (stopIndex === -1) return;

        // Remove the stop
        stops.splice(stopIndex, 1);

        // Recalculate nextTravel for previous stop
        if (stopIndex > 0 && stopIndex < stops.length) {
          // There's a stop after the removed one - update previous stop's nextTravel
          stops[stopIndex - 1] = {
            ...stops[stopIndex - 1],
            nextTravel: {
              type: "drive",
              duration: "15 min",
              mode: "taxi",
              label: "Book Grab",
              price: "50k VND",
              bookable: true,
            },
          };
        } else if (stopIndex > 0) {
          // Removed last stop - clear previous stop's nextTravel
          stops[stopIndex - 1] = {
            ...stops[stopIndex - 1],
            nextTravel: undefined,
          };
        }

        items[dayIndex] = {
          ...items[dayIndex],
          stops,
        };
        set({ itineraryItems: items });

        // Clear route cache for this day
        const routeCache = { ...get().routeCache };
        delete routeCache[dayIndex];
        set({ routeCache });
      },

      /**
       * Update a specific stop
       * @param {number} dayIndex - Index of the day
       * @param {string} stopId - ID of the stop
       * @param {Object} updates - Updates to apply
       */
      updateStop: (dayIndex, stopId, updates) => {
        const items = [...get().itineraryItems];
        if (items[dayIndex]) {
          const stopIndex = items[dayIndex].stops.findIndex(
            (s) => s.id === stopId
          );

          if (stopIndex !== -1) {
            items[dayIndex].stops[stopIndex] = {
              ...items[dayIndex].stops[stopIndex],
              ...updates,
            };
            set({ itineraryItems: items });
          }
        }
      },

      /**
       * Add destination to itinerary with automatic travel management
       * @param {number} dayIndex - Day to add to
       * @param {Object} destination - Destination to add
       */
      addDestinationToItinerary: (dayIndex, destination) => {
        const items = [...get().itineraryItems];
        if (!items[dayIndex]) return;

        const stops = [...items[dayIndex].stops];
        const newStopId = `dest-${Date.now()}`;

        // Create new stop
        const newStop = {
          id: newStopId,
          time: "TBD", // TODO: Calculate based on previous stop
          type: "destination",
          destinationId: destination.id,
          destination: destination,
          isBooked: false,
          bookingDetails: {
            type: "ticket",
            bookable: true,
          },
        };

        // Find insertion point (before last stop or at end)
        const insertIndex = stops.length;

        // Update previous stop's nextTravel if exists
        if (insertIndex > 0) {
          stops[insertIndex - 1] = {
            ...stops[insertIndex - 1],
            nextTravel: {
              type: "drive",
              duration: "15 min",
              mode: "taxi",
              label: "Book Grab",
              price: "50k VND",
              bookable: true,
            },
          };
        }

        // Insert new stop
        stops.splice(insertIndex, 0, newStop);

        items[dayIndex] = { ...items[dayIndex], stops };
        set({ itineraryItems: items });

        // Clear route cache
        const routeCache = { ...get().routeCache };
        delete routeCache[dayIndex];
        set({ routeCache });
      },

      // ========== Plan Management Actions (migrated from PlanContext) ==========

      /**
       * Add item to plan
       * @param {Object} place - Place object to add
       */
      addItem: (place) => {
        const { plan } = get();

        // Support both old format (id) and new format (place_id)
        const placeId = place.place_id || place.id;

        // Check if item already exists
        const exists = plan.items.some(
          (item) => item.placeId === placeId || item.place_id === placeId
        );
        if (exists) {
          console.log("Item already in plan:", place.name);
          return;
        }

        // Handle both formats: {location: {lat, lng}} and {lat, lng}
        const lat = place.lat || place.location?.lat;
        const lng = place.lng || place.location?.lng;

        const newItem = {
          itemId: `item-${Date.now()}`,
          item_id: `item-${Date.now()}`, // Support both naming conventions
          placeId: placeId,
          place_id: placeId, // Support both naming conventions
          name: place.name,
          category: place.category || place.type || "Place",
          lat: lat,
          lng: lng,
          order: plan.items.length,
          addedAt: new Date().toISOString(),
          added_at: new Date(), // Support both naming conventions
          notes: null,
          // Include full place data for rendering
          destination: {
            name: place.name,
            type: place.category || place.type,
            image: place.image,
            rating: place.rating,
            reviews: place.reviews,
            description: place.description,
          },
        };

        set({
          plan: {
            ...plan,
            items: [...plan.items, newItem],
            isOptimized: false,
          },
        });
      },

      /**
       * Remove item from plan
       * @param {string} itemId - ID of the item to remove
       */
      removeItem: (itemId) => {
        const { plan } = get();
        set({
          plan: {
            ...plan,
            items: plan.items
              .filter((item) => item.itemId !== itemId)
              .map((item, index) => ({ ...item, order: index })),
            isOptimized: false,
          },
        });
      },

      /**
       * Reorder plan items (for drag & drop)
       * @param {Array} newItems - Reordered items array
       */
      reorderPlanItems: (newItems) => {
        const { plan } = get();
        set({
          plan: {
            ...plan,
            items: newItems.map((item, index) => ({ ...item, order: index })),
            isOptimized: false,
          },
        });
      },

      /**
       * Replace item in plan
       * @param {string} itemId - ID of the item to replace
       * @param {Object} newPlace - New place object
       */
      replaceItem: (itemId, newPlace) => {
        const { plan } = get();
        set({
          plan: {
            ...plan,
            items: plan.items.map((item) =>
              item.itemId === itemId
                ? {
                  ...item,
                  placeId: newPlace.id,
                  name: newPlace.name,
                  category: newPlace.type || "Place",
                  lat: newPlace.location.lat,
                  lng: newPlace.location.lng,
                  destination: newPlace,
                }
                : item
            ),
            isOptimized: false,
          },
        });
      },

      /**
       * Optimize route using GraphHopper Optimization API
       */
      optimizeRoute: async () => {
        const { plan } = get();

        if (plan.items.length < 2) {
          console.warn("Need at least 2 places to optimize");
          return;
        }

        set({
          plan: { ...plan, isOptimizing: true },
        });

        try {
          const { optimizeRouteSimple } = await import("../apis/graphhopper");

          // Prepare waypoints for optimization
          const waypoints = plan.items.map((item) => ({
            id: item.itemId,
            name: item.name,
            lat: item.lat,
            lng: item.lng,
          }));

          // Call GraphHopper optimization
          const result = await optimizeRouteSimple(waypoints, "car");

          if (result && result.order) {
            // Reorder items based on optimized order
            const optimizedItems = result.order.map((index) => ({
              ...plan.items[index],
              order: result.order.indexOf(index),
            }));

            set({
              plan: {
                ...plan,
                items: optimizedItems,
                isOptimized: true,
                isOptimizing: false,
                totalDistanceKm: (result.distance / 1000).toFixed(2), // Convert meters to km
                estimatedDurationMin: Math.round(
                  (result.distance / 1000 / 40) * 60
                ), // Estimate: 40km/h avg speed
              },
            });
          } else {
            // Fallback if optimization fails
            set({
              plan: {
                ...plan,
                isOptimized: false,
                isOptimizing: false,
              },
            });
          }
        } catch (error) {
          console.error("Optimization error:", error);
          set({
            plan: {
              ...plan,
              isOptimized: false,
              isOptimizing: false,
            },
          });
        }
      },

      /**
       * Clear all plan items
       */
      clearPlan: () => {
        set({
          plan: {
            planId: "default-plan",
            items: [],
            isOptimized: false,
            isOptimizing: false,
            totalDistanceKm: 0,
            estimatedDurationMin: 0,
          },
        });
      },

      // ========== Backend API Integration ==========

      /**
       * Fetch all itineraries from backend
       * @param {string} userId - User ID
       */
      fetchItineraries: async (userId) => {
        try {
          set({ isLoading: true, error: null });
          const itineraries = await fetchUserItinerariesAPI(userId);

          // If there are itineraries, fetch the first one with full details
          if (itineraries && itineraries.length > 0) {
            const firstItinerary = await fetchItineraryByIdAPI(
              itineraries[0].id,
              userId
            );

            // Transform backend data to frontend format
            if (firstItinerary?.days) {
              set({
                itineraryItems: firstItinerary.days,
                currentItinerary: firstItinerary, // Store full itinerary metadata
                isLoading: false,
                error: null,
              });
            }
          } else {
            set({
              itineraryItems: [],
              currentItinerary: null,
              isLoading: false,
            });
          }
        } catch (error) {
          console.error("Error fetching itineraries:", error);
          set({ error: error.message, isLoading: false });
        }
      },

      /**
       * Create a new itinerary in backend
       * @param {Object} itineraryData - Itinerary data
       * @param {string} userId - User ID
       * @returns {Promise<string>} Created itinerary ID
       */
      createNewItinerary: async (itineraryData, userId) => {
        try {
          set({ isLoading: true });
          const response = await createItineraryAPI(itineraryData, userId);
          const itineraryId = response?.itinerary?.id;

          if (itineraryId) {
            // Refresh itineraries list
            await get().fetchItineraries(userId);
          }

          set({ isLoading: false });
          return itineraryId;
        } catch (error) {
          console.error("Error creating itinerary:", error);
          set({ error: error.message, isLoading: false });
          throw error;
        }
      },

      /**
       * Delete an itinerary from backend
       * @param {string} itineraryId - Itinerary ID
       * @param {string} userId - User ID
       */
      deleteItinerary: async (itineraryId, userId) => {
        try {
          await deleteItineraryAPI(itineraryId, userId);
          // Refresh itineraries list
          await get().fetchItineraries(userId);
        } catch (error) {
          console.error("Error deleting itinerary:", error);
          set({ error: error.message });
        }
      },

      /**
       * Add a stop to backend and update local state
       * @param {string} itineraryId - Itinerary ID
       * @param {number} dayIndex - Day index (0-based for frontend)
       * @param {Object} stopData - Stop data
       * @param {string} userId - User ID
       */
      addStopToBackend: async (itineraryId, dayIndex, stopData, userId) => {
        try {
          // Convert frontend format to backend format
          const backendStopData = {
            place_id: stopData.place_id,
            day_index: dayIndex + 1, // Backend uses 1-indexed
            order_index:
              (get().itineraryItems[dayIndex]?.stops?.length || 0) + 1,
            arrival_time: stopData.arrival_time,
            stay_minutes: stopData.stay_minutes || 60,
            notes: stopData.notes || "",
            tags: stopData.tags || [],
            snapshot: stopData.snapshot,
          };

          const response = await addStopAPI(
            itineraryId,
            backendStopData,
            userId
          );

          if (response?.stop) {
            // Update local state
            const items = [...get().itineraryItems];
            if (items[dayIndex]) {
              items[dayIndex] = {
                ...items[dayIndex],
                stops: [...(items[dayIndex].stops || []), response.stop],
              };
              set({ itineraryItems: items });

              // Clear route cache
              const routeCache = { ...get().routeCache };
              delete routeCache[dayIndex];
              set({ routeCache });
            }
          }

          return response;
        } catch (error) {
          console.error("Error adding stop:", error);
          throw error;
        }
      },

      /**
       * Update a stop in backend and local state
       * @param {string} itineraryId - Itinerary ID
       * @param {number} dayIndex - Day index
       * @param {string} stopId - Stop ID
       * @param {Object} updates - Updates to apply
       * @param {string} userId - User ID
       */
      updateStopBackend: async (
        itineraryId,
        dayIndex,
        stopId,
        updates,
        userId
      ) => {
        try {
          await updateStopAPI(itineraryId, stopId, updates, userId);

          // Update local state
          get().updateStop(dayIndex, stopId, updates);
        } catch (error) {
          console.error("Error updating stop:", error);
          throw error;
        }
      },

      /**
       * Delete a stop from backend and local state
       * @param {string} itineraryId - Itinerary ID
       * @param {number} dayIndex - Day index
       * @param {string} stopId - Stop ID
       * @param {string} userId - User ID
       */
      deleteStopBackend: async (itineraryId, dayIndex, stopId, userId) => {
        try {
          await deleteStopAPI(itineraryId, stopId, userId);

          // Update local state
          get().removeStop(dayIndex, stopId);
        } catch (error) {
          console.error("Error deleting stop:", error);
          throw error;
        }
      },
    }),
    { name: "ItineraryStore" }
  )
);

export default useItineraryStore;
