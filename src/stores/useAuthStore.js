import { create } from "zustand";
import { persist } from "zustand/middleware";

/**
 * Auth Store - Manages user authentication state
 * Persists user data to localStorage
 * Uses real user data from Google OAuth login
 */
const useAuthStore = create(
  persist(
    (set, get) => ({
      // ========== State ==========
      user: null, // Current logged-in user
      isAuthenticated: false,
      isLoading: false,

      // ========== Actions ==========

      /**
       * Set user after successful login
       * @param {Object} userData - User data from Google OAuth or other auth provider
       * Expected format: { userId/id, email, fullName/name, avatarUrl/picture, sessionId? }
       */
      setUser: (userData) => {
        set({
          user: userData,
          isAuthenticated: !!userData,
          isLoading: false,
        });
      },

      /**
       * Clear user data on logout
       */
      logout: () => {
        set({
          user: null,
          isAuthenticated: false,
          isLoading: false,
        });
      },

      /**
       * Set loading state
       */
      setLoading: (isLoading) => set({ isLoading }),

      // ========== Helpers ==========

      /**
       * Get current user ID
       * @returns {string|null} User ID or null if not authenticated
       */
      getUserId: () => {
        const state = get();
        return state.user?.userId || state.user?.id || null;
      },

      /**
       * Get current user email
       * @returns {string|null} User email or null if not authenticated
       */
      getUserEmail: () => {
        const state = get();
        return state.user?.email || null;
      },

      /**
       * Get current user full name
       * @returns {string|null} User full name or null if not authenticated
       */
      getUserName: () => {
        const state = get();
        return state.user?.fullName || state.user?.name || null;
      },

      /**
       * Get current user avatar URL
       * @returns {string|null} Avatar URL or null if not authenticated
       */
      getUserAvatar: () => {
        const state = get();
        return state.user?.avatarUrl || state.user?.picture || null;
      },

      /**
       * Get session ID for chat
       * @returns {string|null} Session ID or null if not available
       */
      getSessionId: () => {
        const state = get();
        return state.user?.sessionId || null;
      },
    }),
    {
      name: "auth-storage", // localStorage key
      // Only persist user data, not loading state
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

export default useAuthStore;
