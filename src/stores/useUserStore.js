import { create } from "zustand";
import { devtools, persist } from "zustand/middleware";

/**
 * Zustand Store for User Management
 * Handles user profile, preferences, location, and settings
 */
const useUserStore = create(
  devtools(
    persist(
      (set, get) => ({
        // ========== State ==========
        user: null,
        preferences: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,

        // ========== Actions ==========

        /**
         * Set user profile
         * @param {Object} userData - User profile data
         */
        setUser: (userData) =>
          set({
            user: userData,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          }),

        /**
         * Update user profile
         * @param {Object} updates - Fields to update
         */
        updateProfile: (updates) => {
          const user = get().user;
          if (user) {
            set({
              user: {
                ...user,
                ...updates,
                updatedAt: new Date().toISOString(),
              },
            });
          }
        },

        /**
         * Update user location
         * @param {Object} location - Location object with lat, lng
         */
        updateLocation: (location) => {
          const user = get().user;
          if (user) {
            set({
              user: {
                ...user,
                location,
                lastLocationUpdate: new Date().toISOString(),
              },
            });
          }
        },

        /**
         * Set user preferences
         * @param {Object} preferences - User preferences data
         */
        setPreferences: (preferences) => set({ preferences }),

        /**
         * Update specific preference
         * @param {string} key - Preference key
         * @param {any} value - New value
         */
        updatePreference: (key, value) => {
          const preferences = get().preferences;
          if (preferences) {
            set({
              preferences: {
                ...preferences,
                [key]: value,
              },
            });
          }
        },

        /**
         * Update notification settings
         * @param {Object} notificationSettings - Notification settings object
         */
        updateNotifications: (notificationSettings) => {
          const preferences = get().preferences;
          if (preferences) {
            set({
              preferences: {
                ...preferences,
                notifications: {
                  ...preferences.notifications,
                  ...notificationSettings,
                },
              },
            });
          }
        },

        /**
         * Add saved location
         * @param {Object} location - Location object with name, lat, lng
         */
        addSavedLocation: (location) => {
          const preferences = get().preferences;
          if (preferences) {
            set({
              preferences: {
                ...preferences,
                savedLocations: [
                  ...(preferences.savedLocations || []),
                  location,
                ],
              },
            });
          }
        },

        /**
         * Remove saved location
         * @param {number} index - Index of the location to remove
         */
        removeSavedLocation: (index) => {
          const preferences = get().preferences;
          if (preferences && preferences.savedLocations) {
            set({
              preferences: {
                ...preferences,
                savedLocations: preferences.savedLocations.filter(
                  (_, i) => i !== index
                ),
              },
            });
          }
        },

        /**
         * Add to recent searches
         * @param {string} searchTerm - Search term to add
         */
        addRecentSearch: (searchTerm) => {
          const preferences = get().preferences;
          if (preferences) {
            const recentSearches = preferences.recentSearches || [];
            // Keep only the last 10 searches, avoid duplicates
            const updated = [
              searchTerm,
              ...recentSearches.filter((s) => s !== searchTerm),
            ].slice(0, 10);

            set({
              preferences: {
                ...preferences,
                recentSearches: updated,
              },
            });
          }
        },

        /**
         * Clear recent searches
         */
        clearRecentSearches: () => {
          const preferences = get().preferences;
          if (preferences) {
            set({
              preferences: {
                ...preferences,
                recentSearches: [],
              },
            });
          }
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
         * Logout user
         */
        logout: () =>
          set({
            user: null,
            preferences: null,
            isAuthenticated: false,
            error: null,
          }),

        /**
         * Get user's preferred language
         * @returns {string} Language code (default: 'en')
         */
        getPreferredLanguage: () => {
          return get().preferences?.preferredLanguage || "en";
        },

        /**
         * Get user's travel style
         * @returns {string} Travel style (default: 'balanced')
         */
        getTravelStyle: () => {
          return get().preferences?.travelStyle || "balanced";
        },

        /**
         * Check if user has preference enabled
         * @param {string} preference - Preference to check
         * @returns {boolean}
         */
        hasPreference: (preference) => {
          const preferences = get().preferences;
          return preferences?.[preference] || false;
        },
      }),
      {
        name: "user-storage", // localStorage key
        partialize: (state) => ({
          user: state.user,
          preferences: state.preferences,
          isAuthenticated: state.isAuthenticated,
        }),
      }
    ),
    { name: "UserStore" }
  )
);

export default useUserStore;
