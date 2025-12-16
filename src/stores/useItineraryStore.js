import { create } from "zustand";
import { devtools } from "zustand/middleware";

/**
 * Zustand Store for Itinerary Management
 * Handles itinerary data, bookings, highlights, and route information
 */
const useItineraryStore = create(
  devtools(
    (set, get) => ({
      // ========== State ==========
      itineraryItems: [],
      isLoading: false,
      error: null,
      activeBooking: null, // Currently booking stop { dayIndex, stopId }
      lastBookedStopId: null, // For highlighting
      routeCache: {}, // Cache routes per day: { dayIndex: routeData }

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
        if (items[dayIndex]) {
          items[dayIndex] = {
            ...items[dayIndex],
            stops: items[dayIndex].stops.filter((s) => s.id !== stopId),
          };
          set({ itineraryItems: items });

          // Clear route cache for this day
          const routeCache = { ...get().routeCache };
          delete routeCache[dayIndex];
          set({ routeCache });
        }
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
    }),
    { name: "ItineraryStore" }
  )
);

export default useItineraryStore;
