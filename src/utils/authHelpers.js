import useAuthStore from "../stores/useAuthStore";
import { HARDCODED_TEST_USER } from "./constants";

/**
 * Get current user ID with fallback
 * Priority: 1. Passed parameter, 2. Auth store user, 3. Hardcoded test user
 *
 * @param {string} [userId] - Optional user ID parameter
 * @returns {string} User ID
 *
 * @example
 * // Use in API calls
 * const userId = getCurrentUserId();
 * await fetchItineraries(userId);
 *
 * // Or pass explicit userId
 * await fetchItineraries(getCurrentUserId(customUserId));
 */
export const getCurrentUserId = (userId) => {
  // Priority 1: Use provided userId if available
  if (userId) return userId;

  // Priority 2: Try to get from auth store (real logged-in user)
  try {
    const authUserId = useAuthStore.getState().getUserId();
    if (authUserId && authUserId !== HARDCODED_TEST_USER.userId) {
      return authUserId;
    }
  } catch (error) {
    console.warn("Failed to get user from auth store:", error);
  }

  // Priority 3: Fallback to hardcoded test user for development
  return HARDCODED_TEST_USER.userId;
};

/**
 * Get current user session ID for chat
 *
 * @param {string} [sessionId] - Optional session ID parameter
 * @returns {string} Session ID
 */
export const getCurrentSessionId = (sessionId) => {
  if (sessionId) return sessionId;

  try {
    return useAuthStore.getState().getSessionId();
  } catch (error) {
    return HARDCODED_TEST_USER.sessionId;
  }
};

/**
 * Check if user is authenticated (not using test user)
 * @returns {boolean}
 */
export const isRealUser = () => {
  try {
    const { isAuthenticated, user } = useAuthStore.getState();
    return isAuthenticated && user?.userId !== HARDCODED_TEST_USER.userId;
  } catch (error) {
    return false;
  }
};
