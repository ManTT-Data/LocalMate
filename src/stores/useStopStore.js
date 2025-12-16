import { create } from "zustand";
import { devtools } from "zustand/middleware";

/**
 * Zustand Store for Stop/ItineraryStop Management
 * Handles individual stops, destinations, and related data
 */
const useStopStore = create(
  devtools(
    (set, get) => ({
      // ========== State ==========
      stops: [], // All available stops/destinations
      activeStop: null, // Currently selected/active stop
      stopCache: {}, // Cache for stop details by ID
      isLoading: false,
      error: null,
      filters: {
        type: null, // Filter by type (restaurant, sightseeing, etc.)
        rating: null, // Minimum rating filter
        priceRange: null, // Price range filter
        openNow: false, // Show only open places
      },

      // ========== Actions ==========

      /**
       * Set all stops
       * @param {Array} stops - Array of stop objects
       */
      setStops: (stops) => {
        set({ stops, isLoading: false, error: null });
        // Update cache
        const cache = {};
        stops.forEach((stop) => {
          cache[stop.id] = stop;
        });
        set({ stopCache: { ...get().stopCache, ...cache } });
      },

      /**
       * Set loading state
       */
      setLoading: (isLoading) => set({ isLoading }),

      /**
       * Set error state
       */
      setError: (error) => set({ error, isLoading: false }),

      /**
       * Get stop by ID
       * @param {string} stopId - ID of the stop
       * @returns {Object|null} Stop object or null
       */
      getStopById: (stopId) => {
        // First check cache
        const cached = get().stopCache[stopId];
        if (cached) return cached;

        // Then check stops array
        return get().stops.find((stop) => stop.id === stopId) || null;
      },

      /**
       * Add a new stop
       * @param {Object} stopData - Stop data to add
       */
      addStop: (stopData) => {
        const newStop = {
          id: `stop-${Date.now()}`,
          ...stopData,
          createdAt: new Date().toISOString(),
        };

        set({
          stops: [...get().stops, newStop],
          stopCache: { ...get().stopCache, [newStop.id]: newStop },
        });

        return newStop;
      },

      /**
       * Update a stop
       * @param {string} stopId - ID of the stop to update
       * @param {Object} updates - Fields to update
       */
      updateStop: (stopId, updates) => {
        const stops = get().stops.map((stop) =>
          stop.id === stopId
            ? { ...stop, ...updates, updatedAt: new Date().toISOString() }
            : stop
        );

        const updatedStop = stops.find((s) => s.id === stopId);

        set({
          stops,
          stopCache: updatedStop
            ? { ...get().stopCache, [stopId]: updatedStop }
            : get().stopCache,
        });
      },

      /**
       * Remove a stop
       * @param {string} stopId - ID of the stop to remove
       */
      removeStop: (stopId) => {
        set({
          stops: get().stops.filter((stop) => stop.id !== stopId),
        });

        // Remove from cache
        const cache = { ...get().stopCache };
        delete cache[stopId];
        set({ stopCache: cache });
      },

      /**
       * Set active stop
       * @param {string} stopId - ID of the stop to set as active
       */
      setActiveStop: (stopId) => {
        const stop = get().getStopById(stopId);
        set({ activeStop: stop });
      },

      /**
       * Clear active stop
       */
      clearActiveStop: () => set({ activeStop: null }),

      /**
       * Get stops by type
       * @param {string} type - Type of stop (Restaurant, Beach, etc.)
       * @returns {Array} Filtered stops
       */
      getStopsByType: (type) => {
        return get().stops.filter(
          (stop) => stop.type?.toLowerCase() === type.toLowerCase()
        );
      },

      /**
       * Get stops by rating
       * @param {number} minRating - Minimum rating (0-5)
       * @returns {Array} Filtered stops
       */
      getStopsByRating: (minRating) => {
        return get().stops.filter((stop) => stop.rating >= minRating);
      },

      /**
       * Search stops by name
       * @param {string} query - Search query
       * @returns {Array} Matching stops
       */
      searchStops: (query) => {
        const lowerQuery = query.toLowerCase();
        return get().stops.filter(
          (stop) =>
            stop.name?.toLowerCase().includes(lowerQuery) ||
            stop.description?.toLowerCase().includes(lowerQuery)
        );
      },

      /**
       * Get nearby stops
       * @param {Object} location - Location object with lat, lng
       * @param {number} radiusKm - Radius in kilometers (default: 5)
       * @returns {Array} Stops within radius
       */
      getNearbyStops: (location, radiusKm = 5) => {
        return get().stops.filter((stop) => {
          if (!stop.location) return false;

          // Simple distance calculation using Haversine formula
          const R = 6371; // Earth's radius in km
          const dLat = ((stop.location.lat - location.lat) * Math.PI) / 180;
          const dLng = ((stop.location.lng - location.lng) * Math.PI) / 180;

          const a =
            Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos((location.lat * Math.PI) / 180) *
              Math.cos((stop.location.lat * Math.PI) / 180) *
              Math.sin(dLng / 2) *
              Math.sin(dLng / 2);

          const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
          const distance = R * c;

          return distance <= radiusKm;
        });
      },

      /**
       * Get top-rated stops
       * @param {number} limit - Number of stops to return (default: 10)
       * @returns {Array} Top-rated stops
       */
      getTopRatedStops: (limit = 10) => {
        return [...get().stops]
          .sort((a, b) => (b.rating || 0) - (a.rating || 0))
          .slice(0, limit);
      },

      /**
       * Get stops marked as top picks
       * @returns {Array} Top pick stops
       */
      getTopPickStops: () => {
        return get().stops.filter((stop) => stop.isTopPick);
      },

      /**
       * Get currently open stops
       * @returns {Array} Open stops
       */
      getOpenStops: () => {
        return get().stops.filter((stop) => stop.openNow);
      },

      /**
       * Set filters
       * @param {Object} filters - Filter object
       */
      setFilters: (filters) => {
        set({ filters: { ...get().filters, ...filters } });
      },

      /**
       * Clear all filters
       */
      clearFilters: () => {
        set({
          filters: {
            type: null,
            rating: null,
            priceRange: null,
            openNow: false,
          },
        });
      },

      /**
       * Get filtered stops based on current filters
       * @returns {Array} Filtered stops
       */
      getFilteredStops: () => {
        const { stops, filters } = get();
        let filtered = [...stops];

        if (filters.type) {
          filtered = filtered.filter(
            (stop) => stop.type?.toLowerCase() === filters.type.toLowerCase()
          );
        }

        if (filters.rating) {
          filtered = filtered.filter((stop) => stop.rating >= filters.rating);
        }

        if (filters.openNow) {
          filtered = filtered.filter((stop) => stop.openNow);
        }

        return filtered;
      },

      /**
       * Clear all stops
       */
      clearStops: () => set({ stops: [], activeStop: null, stopCache: {} }),
    }),
    { name: "StopStore" }
  )
);

export default useStopStore;
