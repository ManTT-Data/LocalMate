import useAuthStore from "../stores/useAuthStore";

/**
 * Get current user ID from auth store or parameter
 * Priority: 1. Passed parameter, 2. Auth store user
 *
 * @param {string} [userId] - Optional user ID parameter
 * @returns {string|null} User ID or null if not authenticated
 *
 * @example
 * // Use in API calls
 * const userId = getCurrentUserId();
 * if (userId) {
 *   await fetchItineraries(userId);
 * }
 *
 * // Or pass explicit userId
 * await fetchItineraries(getCurrentUserId(customUserId));
 */
export const getCurrentUserId = (userId) => {
  // Priority 1: Use provided userId if available
  if (userId) return userId;

  // Priority 2: Get from auth store (real logged-in user)
  try {
    return useAuthStore.getState().getUserId();
  } catch (error) {
    console.warn("Failed to get user from auth store:", error);
    return null;
  }
};

/**
 * Get current user session ID for chat
 *
 * @param {string} [sessionId] - Optional session ID parameter
 * @returns {string|null} Session ID or null if not available
 */
export const getCurrentSessionId = (sessionId) => {
  if (sessionId) return sessionId;

  try {
    return useAuthStore.getState().getSessionId();
  } catch (error) {
    console.warn("Failed to get session ID from auth store:", error);
    return null;
  }
};

/**
 * Check if user is authenticated with real Google account
 * @returns {boolean}
 */
export const isRealUser = () => {
  try {
    const { isAuthenticated } = useAuthStore.getState();
    return isAuthenticated === true;
  } catch (error) {
    return false;
  }
};
