import { create } from "zustand";
import { persist } from "zustand/middleware";
import { HARDCODED_TEST_USER } from "../utils/constants";

/**
 * Auth Store - Manages user authentication state
 * Persists user data to localStorage
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
       * Get current user ID with fallback to test user
       * Priority: 1. Real user, 2. Test user
       * @returns {string} User ID
       */
      getUserId: () => {
        const state = get();
        if (state.user?.userId) return state.user.userId;
        if (state.user?.id) return state.user.id;
        // Fallback to hardcoded test user for development
        return HARDCODED_TEST_USER.userId;
      },

      /**
       * Get current user email
       * @returns {string} User email
       */
      getUserEmail: () => {
        const state = get();
        return state.user?.email || HARDCODED_TEST_USER.email;
      },

      /**
       * Get current user full name
       * @returns {string} User full name
       */
      getUserName: () => {
        const state = get();
        return (
          state.user?.fullName ||
          state.user?.name ||
          HARDCODED_TEST_USER.fullName
        );
      },

      /**
       * Get current user avatar URL
       * @returns {string} Avatar URL
       */
      getUserAvatar: () => {
        const state = get();
        return (
          state.user?.avatarUrl ||
          state.user?.picture ||
          HARDCODED_TEST_USER.avatarUrl
        );
      },

      /**
       * Get session ID for chat
       * @returns {string} Session ID
       */
      getSessionId: () => {
        const state = get();
        return state.user?.sessionId || HARDCODED_TEST_USER.sessionId;
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
