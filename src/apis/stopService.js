/**
 * Stop Service - Backend API Integration for Itinerary Stops
 * Handles all stop management with persistent database storage (itinerary_stops table)
 */

import apiHelper from "../utils/apiHelper";
import { apiUrls, HARDCODED_TEST_USER } from "../utils/constants";

/**
 * Fetch all stops for a specific itinerary
 * @param {string} itineraryId - Itinerary ID
 * @param {string} userId - User ID
 * @returns {Promise<Array>} List of stops
 */
export const fetchItineraryStopsAPI = async (
  itineraryId,
  userId = HARDCODED_TEST_USER.userId
) => {
  // Stops are included when fetching itinerary
  const response = await apiHelper.get(
    `${apiUrls.itinerary.get(itineraryId)}?user_id=${userId}`
  );
  return response?.itinerary?.stops || [];
};

/**
 * Add a stop to an itinerary
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
  const {
    place_id,
    day_index = 1,
    order_index = 1,
    arrival_time = null,
    stay_minutes = 60,
    notes = null,
    tags = [],
    snapshot = null,
  } = stopData;

  const requestBody = {
    place_id,
    day_index,
    order_index,
    arrival_time,
    stay_minutes,
    notes,
    tags,
    snapshot,
  };

  console.log("📤 Adding stop to itinerary:", {
    itineraryId,
    requestBody,
  });

  const response = await apiHelper.post(
    `${apiUrls.itinerary.addStop(itineraryId)}?user_id=${userId}`,
    requestBody
  );

  return response;
};

/**
 * Update a stop in an itinerary
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
 * Delete a stop from an itinerary
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
 * Reorder stops within a day
 * @param {string} itineraryId - Itinerary ID
 * @param {number} dayIndex - Day index (1-indexed)
 * @param {Array<string>} stopIds - Ordered array of stop IDs
 * @param {string} userId - User ID
 * @returns {Promise<Array>} Updated stops
 */
export const reorderStopsAPI = async (
  itineraryId,
  dayIndex,
  stopIds,
  userId = HARDCODED_TEST_USER.userId
) => {
  // Update each stop's order_index
  const updatePromises = stopIds.map((stopId, index) =>
    updateStopAPI(
      itineraryId,
      stopId,
      {
        day_index: dayIndex,
        order_index: index + 1, // 1-indexed
      },
      userId
    )
  );

  await Promise.all(updatePromises);

  return await fetchItineraryStopsAPI(itineraryId, userId);
};

/**
 * Move a stop to a different day
 * @param {string} itineraryId - Itinerary ID
 * @param {string} stopId - Stop ID
 * @param {number} fromDayIndex - Current day index
 * @param {number} toDayIndex - Target day index
 * @param {number} toOrderIndex - Target order index
 * @param {string} userId - User ID
 * @returns {Promise<Object>} Update result
 */
export const moveStopToDayAPI = async (
  itineraryId,
  stopId,
  fromDayIndex,
  toDayIndex,
  toOrderIndex = 1,
  userId = HARDCODED_TEST_USER.userId
) => {
  const response = await updateStopAPI(
    itineraryId,
    stopId,
    {
      day_index: toDayIndex,
      order_index: toOrderIndex,
    },
    userId
  );

  return response;
};

/**
 * Bulk add stops to an itinerary
 * @param {string} itineraryId - Itinerary ID
 * @param {Array<Object>} stops - Array of stop data
 * @param {string} userId - User ID
 * @returns {Promise<Array>} Created stops
 */
export const bulkAddStopsAPI = async (
  itineraryId,
  stops,
  userId = HARDCODED_TEST_USER.userId
) => {
  const createPromises = stops.map((stopData) =>
    addStopAPI(itineraryId, stopData, userId)
  );

  const results = await Promise.all(createPromises);
  return results;
};

/**
 * Get stops for a specific day
 * @param {string} itineraryId - Itinerary ID
 * @param {number} dayIndex - Day index (1-indexed)
 * @param {string} userId - User ID
 * @returns {Promise<Array>} Stops for the day
 */
export const fetchDayStopsAPI = async (
  itineraryId,
  dayIndex,
  userId = HARDCODED_TEST_USER.userId
) => {
  const allStops = await fetchItineraryStopsAPI(itineraryId, userId);
  return allStops
    .filter((stop) => stop.day_index === dayIndex)
    .sort((a, b) => a.order_index - b.order_index);
};

/**
 * Update stop timing
 * @param {string} itineraryId - Itinerary ID
 * @param {string} stopId - Stop ID
 * @param {string} arrivalTime - New arrival time (ISO string)
 * @param {number} stayMinutes - Stay duration in minutes
 * @param {string} userId - User ID
 * @returns {Promise<Object>} Update result
 */
export const updateStopTimingAPI = async (
  itineraryId,
  stopId,
  arrivalTime,
  stayMinutes,
  userId = HARDCODED_TEST_USER.userId
) => {
  return await updateStopAPI(
    itineraryId,
    stopId,
    {
      arrival_time: arrivalTime,
      stay_minutes: stayMinutes,
    },
    userId
  );
};

/**
 * Add notes to a stop
 * @param {string} itineraryId - Itinerary ID
 * @param {string} stopId - Stop ID
 * @param {string} notes - Notes to add
 * @param {string} userId - User ID
 * @returns {Promise<Object>} Update result
 */
export const addStopNotesAPI = async (
  itineraryId,
  stopId,
  notes,
  userId = HARDCODED_TEST_USER.userId
) => {
  return await updateStopAPI(
    itineraryId,
    stopId,
    {
      notes,
    },
    userId
  );
};

/**
 * Add tags to a stop
 * @param {string} itineraryId - Itinerary ID
 * @param {string} stopId - Stop ID
 * @param {Array<string>} tags - Tags to add
 * @param {string} userId - User ID
 * @returns {Promise<Object>} Update result
 */
export const addStopTagsAPI = async (
  itineraryId,
  stopId,
  tags,
  userId = HARDCODED_TEST_USER.userId
) => {
  return await updateStopAPI(
    itineraryId,
    stopId,
    {
      tags,
    },
    userId
  );
};

/**
 * Get statistics for stops in an itinerary
 * @param {string} itineraryId - Itinerary ID
 * @param {string} userId - User ID
 * @returns {Promise<Object>} Stop statistics
 */
export const getStopStatsAPI = async (
  itineraryId,
  userId = HARDCODED_TEST_USER.userId
) => {
  const stops = await fetchItineraryStopsAPI(itineraryId, userId);

  const totalStops = stops.length;
  const totalDuration = stops.reduce(
    (sum, stop) => sum + (stop.stay_minutes || 0),
    0
  );

  // Group by category
  const byCategory = stops.reduce((acc, stop) => {
    const category = stop.snapshot?.category || "Other";
    acc[category] = (acc[category] || 0) + 1;
    return acc;
  }, {});

  // Group by day
  const byDay = stops.reduce((acc, stop) => {
    const day = stop.day_index;
    if (!acc[day]) acc[day] = [];
    acc[day].push(stop);
    return acc;
  }, {});

  return {
    totalStops,
    totalDuration,
    totalDurationFormatted: `${Math.floor(totalDuration / 60)}h ${
      totalDuration % 60
    }m`,
    byCategory,
    byDay,
    daysWithStops: Object.keys(byDay).length,
  };
};

// Export all functions
export default {
  fetchItineraryStopsAPI,
  addStopAPI,
  updateStopAPI,
  deleteStopAPI,
  reorderStopsAPI,
  moveStopToDayAPI,
  bulkAddStopsAPI,
  fetchDayStopsAPI,
  updateStopTimingAPI,
  addStopNotesAPI,
  addStopTagsAPI,
  getStopStatsAPI,
};
