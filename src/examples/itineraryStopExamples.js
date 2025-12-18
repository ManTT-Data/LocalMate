/**
 * Example: How to add stop directly to itinerary_stops table
 *
 * File này demo cách sử dụng currentItineraryId để add stops
 * mà KHÔNG CẦN fetch lại toàn bộ itinerary
 */

import { addStopAPI } from "../apis/stopService";
import { HARDCODED_TEST_USER } from "../utils/constants";

/**
 * Ví dụ 1: Thêm destination từ map
 */
export const addDestinationFromMap = async (
  currentItineraryId,
  destination,
  dayIndex = 0 // Frontend uses 0-indexed
) => {
  if (!currentItineraryId) {
    throw new Error("No itinerary ID available");
  }

  const stopData = {
    place_id: destination.place_id || destination.id,
    day_index: dayIndex + 1, // Backend uses 1-indexed
    order_index: 1, // Will be auto-calculated on backend
    arrival_time: null, // Can be calculated later
    stay_minutes: 60, // Default 1 hour
    notes: "",
    tags: destination.tags || [],
    snapshot: {
      name: destination.name,
      category: destination.category || destination.type,
      address: destination.address,
      rating: destination.rating,
      image: destination.image,
    },
  };

  try {
    // ✅ Add trực tiếp vào itinerary_stops
    const response = await addStopAPI(
      currentItineraryId,
      stopData,
      HARDCODED_TEST_USER.userId
    );

    console.log("✅ Added stop to itinerary:", response);
    return response;
  } catch (error) {
    console.error("❌ Error adding stop:", error);
    throw error;
  }
};

/**
 * Ví dụ 2: Thêm nhiều stops cùng lúc (bulk add)
 */
export const addMultipleStops = async (
  currentItineraryId,
  destinations,
  dayIndex = 0
) => {
  if (!currentItineraryId) {
    throw new Error("No itinerary ID available");
  }

  const { bulkAddStopsAPI } = await import("../apis/stopService");

  const stopsData = destinations.map((dest, index) => ({
    place_id: dest.place_id || dest.id,
    day_index: dayIndex + 1,
    order_index: index + 1,
    arrival_time: null,
    stay_minutes: dest.duration || 60,
    notes: dest.notes || "",
    tags: dest.tags || [],
    snapshot: {
      name: dest.name,
      category: dest.category,
      rating: dest.rating,
    },
  }));

  try {
    // ✅ Bulk add vào itinerary_stops
    const responses = await bulkAddStopsAPI(
      currentItineraryId,
      stopsData,
      HARDCODED_TEST_USER.userId
    );

    console.log(`✅ Added ${responses.length} stops to itinerary`);
    return responses;
  } catch (error) {
    console.error("❌ Error bulk adding stops:", error);
    throw error;
  }
};

/**
 * Ví dụ 3: Update stop (change time, notes, etc.)
 */
export const updateStopDetails = async (
  currentItineraryId,
  stopId,
  updates
) => {
  if (!currentItineraryId) {
    throw new Error("No itinerary ID available");
  }

  const { updateStopAPI } = await import("../apis/stopService");

  try {
    // ✅ Update trực tiếp trong itinerary_stops
    const response = await updateStopAPI(
      currentItineraryId,
      stopId,
      updates,
      HARDCODED_TEST_USER.userId
    );

    console.log("✅ Updated stop:", response);
    return response;
  } catch (error) {
    console.error("❌ Error updating stop:", error);
    throw error;
  }
};

/**
 * Ví dụ 4: Delete stop
 */
export const removeStop = async (currentItineraryId, stopId) => {
  if (!currentItineraryId) {
    throw new Error("No itinerary ID available");
  }

  const { deleteStopAPI } = await import("../apis/stopService");

  try {
    // ✅ Delete trực tiếp từ itinerary_stops
    await deleteStopAPI(currentItineraryId, stopId, HARDCODED_TEST_USER.userId);

    console.log("✅ Deleted stop:", stopId);
  } catch (error) {
    console.error("❌ Error deleting stop:", error);
    throw error;
  }
};

/**
 * Ví dụ 5: Reorder stops trong một ngày
 */
export const reorderDayStops = async (
  currentItineraryId,
  dayIndex,
  stopIds // Array of stop IDs in new order
) => {
  if (!currentItineraryId) {
    throw new Error("No itinerary ID available");
  }

  const { reorderStopsAPI } = await import("../apis/stopService");

  try {
    // ✅ Reorder stops (backend will update order_index)
    const updatedStops = await reorderStopsAPI(
      currentItineraryId,
      dayIndex + 1, // Convert to 1-indexed
      stopIds,
      HARDCODED_TEST_USER.userId
    );

    console.log("✅ Reordered stops:", updatedStops);
    return updatedStops;
  } catch (error) {
    console.error("❌ Error reordering stops:", error);
    throw error;
  }
};

/**
 * Ví dụ 6: Move stop to different day
 */
export const moveStopToAnotherDay = async (
  currentItineraryId,
  stopId,
  fromDayIndex,
  toDayIndex
) => {
  if (!currentItineraryId) {
    throw new Error("No itinerary ID available");
  }

  const { moveStopToDayAPI } = await import("../apis/stopService");

  try {
    // ✅ Move stop to different day
    const response = await moveStopToDayAPI(
      currentItineraryId,
      stopId,
      fromDayIndex + 1, // Convert to 1-indexed
      toDayIndex + 1, // Convert to 1-indexed
      1, // Default order_index
      HARDCODED_TEST_USER.userId
    );

    console.log(
      `✅ Moved stop from Day ${fromDayIndex + 1} to Day ${toDayIndex + 1}`
    );
    return response;
  } catch (error) {
    console.error("❌ Error moving stop:", error);
    throw error;
  }
};

// Export all examples
export default {
  addDestinationFromMap,
  addMultipleStops,
  updateStopDetails,
  removeStop,
  reorderDayStops,
  moveStopToAnotherDay,
};
