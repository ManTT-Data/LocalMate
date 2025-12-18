/**
 * Itinerary Service - Backend API Integration
 * Handles all itinerary management with persistent database storage
 */

import apiHelper from "../utils/apiHelper";
import { apiUrls, HARDCODED_TEST_USER } from "../utils/constants";
import {
  transformBackendToFrontend,
  transformStopToBackend,
  createItineraryRequest,
  calculateTotalDays,
} from "../utils/itineraryHelpers";

/**
 * Fetch all itineraries for a user
 * @param {string} userId - User ID
 * @returns {Promise<Array>} List of itineraries
 */
export const fetchUserItinerariesAPI = async (
  userId = HARDCODED_TEST_USER.userId
) => {
  const response = await apiHelper.get(
    `${apiUrls.itinerary.list}?user_id=${userId}`
  );
  return response;
};

/**
 * Fetch single itinerary by ID with all stops
 * @param {string} itineraryId - Itinerary ID
 * @param {string} userId - User ID
 * @returns {Promise<Object>} Itinerary with stops in frontend format
 */
export const fetchItineraryByIdAPI = async (
  itineraryId,
  userId = HARDCODED_TEST_USER.userId
) => {
  const response = await apiHelper.get(
    `${apiUrls.itinerary.get(itineraryId)}?user_id=${userId}`
  );

  if (response?.itinerary) {
    // Transform backend format to frontend format
    const frontendItinerary = transformBackendToFrontend(response.itinerary);
    return {
      ...response.itinerary,
      days: frontendItinerary,
    };
  }

  return response;
};

/**
 * Fetch itinerary data from backend (legacy method for compatibility)
 * @param {string} userId - User ID (optional)
 * @returns {Promise<Array>} Itinerary items in frontend format
 */
export const fetchItineraryFromBackend = async (userId = "anonymous") => {
  try {
    const itineraries = await fetchUserItinerariesAPI(userId);

    if (itineraries && itineraries.length > 0) {
      // Get the first (most recent) itinerary
      const firstItinerary = await fetchItineraryByIdAPI(
        itineraries[0].id,
        userId
      );
      return firstItinerary.days || [];
    }

    // Return empty array if no itineraries
    return [];
  } catch (error) {
    console.error("Error fetching itinerary:", error);
    throw error;
  }
};

/**
 * Create a new itinerary
 * @param {Object} itineraryData - Itinerary data
 * @param {string} userId - User ID (defaults to test user)
 * @returns {Promise<Object>} Created itinerary
 */
export const createItineraryAPI = async (
  itineraryData,
  userId = HARDCODED_TEST_USER.userId
) => {
  const {
    title = "My Trip to Da Nang",
    startDate,
    endDate,
    totalBudget,
    currency = "VND",
  } = itineraryData;

  const totalDays = calculateTotalDays(startDate, endDate);

  const request = createItineraryRequest({
    title,
    startDate,
    endDate,
    totalDays,
    totalBudget,
    currency,
  });

  const response = await apiHelper.post(
    `${apiUrls.itinerary.create}?user_id=${userId}`,
    request
  );

  return response;
};

/**
 * Update itinerary details
 * @param {string} itineraryId - Itinerary ID
 * @param {Object} updates - Fields to update
 * @param {string} userId - User ID
 * @returns {Promise<Object>} Update result
 */
export const updateItineraryAPI = async (
  itineraryId,
  updates,
  userId = HARDCODED_TEST_USER.userId
) => {
  const response = await apiHelper.put(
    `${apiUrls.itinerary.update(itineraryId)}?user_id=${userId}`,
    updates
  );

  return response;
};

/**
 * Delete an itinerary
 * @param {string} itineraryId - Itinerary ID
 * @param {string} userId - User ID
 * @returns {Promise<Object>} Delete result
 */
export const deleteItineraryAPI = async (
  itineraryId,
  userId = HARDCODED_TEST_USER.userId
) => {
  const response = await apiHelper.delete(
    `${apiUrls.itinerary.delete(itineraryId)}?user_id=${userId}`
  );

  return response;
};

/**
 * Add a stop to the itinerary
 * @param {string} itineraryId - Itinerary ID
 * @param {Object} stopData - Stop data
 * @param {string} userId - User ID
 * @returns {Promise<Object>} Created stop
 */
export const addStopAPI = async (
  itineraryId,
  stopData,
  userId = HARDCODED_TEST_USER.userId
) => {
  const { destination, dayIndex, orderIndex, time, stayMinutes, notes, tags } =
    stopData;

  const backendStop = transformStopToBackend(
    {
      destinationId: destination?.id || destination?.place_id,
      time,
      stayMinutes,
      notes,
      tags,
    },
    dayIndex,
    orderIndex,
    itineraryId
  );

  const response = await apiHelper.post(
    `${apiUrls.itinerary.addStop(itineraryId)}?user_id=${userId}`,
    backendStop
  );

  return response;
};

/**
 * Update a stop in the itinerary
 * @param {string} itineraryId - Itinerary ID
 * @param {string} stopId - Stop ID
 * @param {Object} updates - Fields to update
 * @param {string} userId - User ID
 * @returns {Promise<Object>} Update result
 */
export const updateStopAPI = async (
  itineraryId,
  stopId,
  updates,
  userId = HARDCODED_TEST_USER.userId
) => {
  const response = await apiHelper.put(
    `${apiUrls.itinerary.updateStop(itineraryId, stopId)}?user_id=${userId}`,
    updates
  );

  return response;
};

/**
 * Delete a stop from the itinerary
 * @param {string} itineraryId - Itinerary ID
 * @param {string} stopId - Stop ID
 * @param {string} userId - User ID
 * @returns {Promise<Object>} Delete result
 */
export const deleteStopAPI = async (
  itineraryId,
  stopId,
  userId = HARDCODED_TEST_USER.userId
) => {
  const response = await apiHelper.delete(
    `${apiUrls.itinerary.deleteStop(itineraryId, stopId)}?user_id=${userId}`
  );

  return response;
};

/**
 * Book a service (Grab, ticket, reservation)
 * @param {string} stopId - ID of the stop
 * @param {string} serviceType - Type of service (grab, ticket, reservation)
 * @param {Object} details - Booking details
 * @returns {Promise<Object>} Booking confirmation
 *
 * @deprecated This function should be moved to bookingService once backend is implemented
 */
export const bookServiceAPI = async (stopId, serviceType, details = {}) => {
  // This is a placeholder - booking functionality needs to be implemented in backend
  console.warn(
    "bookServiceAPI is deprecated - booking backend not yet implemented"
  );

  // Simulate delay
  await new Promise((resolve) => setTimeout(resolve, 1000));

  // Return mock response
  return {
    success: true,
    bookingId: `BK${Date.now()}`,
    stopId,
    serviceType,
    confirmedAt: new Date().toISOString(),
    details: {
      ...details,
      status: "confirmed",
    },
  };
};

/**
 * Cancel a booking
 * @param {string} bookingId - Booking ID to cancel
 * @returns {Promise<Object>} Cancellation confirmation
 *
 * @deprecated This function should be moved to bookingService once backend is implemented
 */
export const cancelBookingAPI = async (bookingId) => {
  // This is a placeholder - booking functionality needs to be implemented in backend
  console.warn(
    "cancelBookingAPI is deprecated - booking backend not yet implemented"
  );

  // Simulate delay
  await new Promise((resolve) => setTimeout(resolve, 500));

  return {
    success: true,
    bookingId,
    cancelledAt: new Date().toISOString(),
    message: "Booking cancelled successfully",
  };
};

// Export all functions
export default {
  fetchUserItinerariesAPI,
  fetchItineraryByIdAPI,
  fetchItineraryFromBackend,
  createItineraryAPI,
  updateItineraryAPI,
  deleteItineraryAPI,
  addStopAPI,
  updateStopAPI,
  deleteStopAPI,
  bookServiceAPI, // Deprecated
  cancelBookingAPI, // Deprecated
};
