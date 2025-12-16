/**
 * Mock Backend Service for Stop/Destination Management
 * Simulates API calls for stops and destinations
 */

import { allStops, destinations } from "../data/mockData";

/**
 * Simulate network delay
 * @param {number} min - Minimum delay in ms
 * @param {number} max - Maximum delay in ms
 */
const simulateDelay = (min = 500, max = 1500) => {
  const delay = Math.floor(Math.random() * (max - min + 1)) + min;
  return new Promise((resolve) => setTimeout(resolve, delay));
};

/**
 * Simulate occasional API failures (10% chance)
 */
const shouldFail = () => Math.random() < 0.1;

/**
 * Fetch all available stops
 * @returns {Promise<Array>} All stops
 */
export const fetchAllStopsAPI = async () => {
  await simulateDelay();

  if (shouldFail()) {
    throw new Error("Failed to fetch stops");
  }

  return allStops;
};

/**
 * Fetch stop by ID
 * @param {string} stopId - Stop ID
 * @returns {Promise<Object>} Stop details
 */
export const fetchStopByIdAPI = async (stopId) => {
  await simulateDelay(300, 800);

  if (shouldFail()) {
    throw new Error("Failed to fetch stop details");
  }

  const stop = allStops.find((s) => s.id === stopId);

  if (!stop) {
    throw new Error("Stop not found");
  }

  // Return stop with additional details
  return {
    ...stop,
    detailedDescription: `${stop.description} This is a popular destination in Da Nang with ${stop.reviews} reviews.`,
    amenities: ["WiFi", "Parking", "Restrooms"],
    accessibility: "Wheelchair accessible",
    bestTimeToVisit: "Morning hours (8-10 AM)",
    lastUpdated: new Date().toISOString(),
  };
};

/**
 * Search stops by query
 * @param {string} query - Search query
 * @returns {Promise<Array>} Matching stops
 */
export const searchStopsAPI = async (query) => {
  await simulateDelay(400, 900);

  if (shouldFail()) {
    throw new Error("Search failed. Please try again.");
  }

  const lowerQuery = query.toLowerCase();
  return allStops.filter(
    (stop) =>
      stop.name?.toLowerCase().includes(lowerQuery) ||
      stop.description?.toLowerCase().includes(lowerQuery) ||
      stop.type?.toLowerCase().includes(lowerQuery)
  );
};

/**
 * Get stops by type/category
 * @param {string} type - Stop type (Restaurant, Beach, Sightseeing, etc.)
 * @returns {Promise<Array>} Stops of the specified type
 */
export const fetchStopsByTypeAPI = async (type) => {
  await simulateDelay(300, 700);

  if (shouldFail()) {
    throw new Error("Failed to fetch stops by type");
  }

  return allStops.filter(
    (stop) => stop.type?.toLowerCase() === type.toLowerCase()
  );
};

/**
 * Get nearby stops based on location
 * @param {number} lat - Latitude
 * @param {number} lng - Longitude
 * @param {number} radiusKm - Radius in kilometers (default: 5)
 * @returns {Promise<Array>} Nearby stops
 */
export const fetchNearbyStopsAPI = async (lat, lng, radiusKm = 5) => {
  await simulateDelay(500, 1000);

  if (shouldFail()) {
    throw new Error("Failed to fetch nearby stops");
  }

  // Calculate distance using Haversine formula
  const calculateDistance = (lat1, lng1, lat2, lng2) => {
    const R = 6371; // Earth's radius in km
    const dLat = ((lat2 - lat1) * Math.PI) / 180;
    const dLng = ((lng2 - lng1) * Math.PI) / 180;

    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos((lat1 * Math.PI) / 180) *
        Math.cos((lat2 * Math.PI) / 180) *
        Math.sin(dLng / 2) *
        Math.sin(dLng / 2);

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  };

  return allStops
    .filter((stop) => {
      if (!stop.location) return false;
      const distance = calculateDistance(
        lat,
        lng,
        stop.location.lat,
        stop.location.lng
      );
      return distance <= radiusKm;
    })
    .map((stop) => ({
      ...stop,
      distance: calculateDistance(
        lat,
        lng,
        stop.location.lat,
        stop.location.lng
      ).toFixed(2),
    }))
    .sort((a, b) => parseFloat(a.distance) - parseFloat(b.distance));
};

/**
 * Get top-rated stops
 * @param {number} limit - Number of stops to return
 * @returns {Promise<Array>} Top-rated stops
 */
export const fetchTopRatedStopsAPI = async (limit = 10) => {
  await simulateDelay(400, 800);

  if (shouldFail()) {
    throw new Error("Failed to fetch top-rated stops");
  }

  return [...allStops]
    .sort((a, b) => (b.rating || 0) - (a.rating || 0))
    .slice(0, limit);
};

/**
 * Get top pick stops
 * @returns {Promise<Array>} Top pick stops
 */
export const fetchTopPickStopsAPI = async () => {
  await simulateDelay(300, 700);

  if (shouldFail()) {
    throw new Error("Failed to fetch top picks");
  }

  return allStops.filter((stop) => stop.isTopPick);
};

/**
 * Create a new stop (for admin/user contributions)
 * @param {Object} stopData - Stop data
 * @returns {Promise<Object>} Created stop
 */
export const createStopAPI = async (stopData) => {
  await simulateDelay(800, 1500);

  if (shouldFail()) {
    throw new Error("Failed to create stop");
  }

  const newStop = {
    id: `stop-${Date.now()}`,
    ...stopData,
    rating: 0,
    reviews: 0,
    createdAt: new Date().toISOString(),
    status: "pending-review",
  };

  return {
    success: true,
    stop: newStop,
    message: "Stop created successfully and pending review",
  };
};

/**
 * Update stop information
 * @param {string} stopId - Stop ID
 * @param {Object} updates - Fields to update
 * @returns {Promise<Object>} Update result
 */
export const updateStopAPI = async (stopId, updates) => {
  await simulateDelay(500, 1000);

  if (shouldFail()) {
    throw new Error("Failed to update stop");
  }

  return {
    success: true,
    stopId,
    updates,
    updatedAt: new Date().toISOString(),
    message: "Stop updated successfully",
  };
};

/**
 * Delete a stop
 * @param {string} stopId - Stop ID
 * @returns {Promise<Object>} Delete result
 */
export const deleteStopAPI = async (stopId) => {
  await simulateDelay(400, 800);

  if (shouldFail()) {
    throw new Error("Failed to delete stop");
  }

  return {
    success: true,
    stopId,
    deletedAt: new Date().toISOString(),
    message: "Stop deleted successfully",
  };
};

/**
 * Get stop reviews
 * @param {string} stopId - Stop ID
 * @returns {Promise<Array>} Reviews for the stop
 */
export const fetchStopReviewsAPI = async (stopId) => {
  await simulateDelay(400, 900);

  if (shouldFail()) {
    throw new Error("Failed to fetch reviews");
  }

  // Return mock reviews
  return [
    {
      id: "review-1",
      userId: "user-123",
      userName: "John Doe",
      rating: 5,
      comment: "Amazing place! Highly recommended.",
      createdAt: "2024-10-15T10:30:00Z",
      helpful: 15,
    },
    {
      id: "review-2",
      userId: "user-456",
      userName: "Jane Smith",
      rating: 4,
      comment: "Great experience, but it was quite crowded.",
      createdAt: "2024-10-14T14:20:00Z",
      helpful: 8,
    },
  ];
};

/**
 * Add review to a stop
 * @param {string} stopId - Stop ID
 * @param {Object} reviewData - Review data
 * @returns {Promise<Object>} Created review
 */
export const addStopReviewAPI = async (stopId, reviewData) => {
  await simulateDelay(600, 1200);

  if (shouldFail()) {
    throw new Error("Failed to submit review");
  }

  const newReview = {
    id: `review-${Date.now()}`,
    stopId,
    ...reviewData,
    createdAt: new Date().toISOString(),
    helpful: 0,
  };

  return {
    success: true,
    review: newReview,
    message: "Review submitted successfully",
  };
};

/**
 * Get stop photos
 * @param {string} stopId - Stop ID
 * @returns {Promise<Array>} Photos for the stop
 */
export const fetchStopPhotosAPI = async (stopId) => {
  await simulateDelay(500, 1000);

  if (shouldFail()) {
    throw new Error("Failed to fetch photos");
  }

  // Return mock photo URLs
  return [
    {
      id: "photo-1",
      url: "https://example.com/photo1.jpg",
      uploadedBy: "user-123",
      uploadedAt: "2024-10-10T12:00:00Z",
      likes: 42,
    },
    {
      id: "photo-2",
      url: "https://example.com/photo2.jpg",
      uploadedBy: "user-456",
      uploadedAt: "2024-10-11T15:30:00Z",
      likes: 28,
    },
  ];
};

/**
 * Get currently open stops
 * @returns {Promise<Array>} Open stops
 */
export const fetchOpenStopsAPI = async () => {
  await simulateDelay(300, 600);

  if (shouldFail()) {
    throw new Error("Failed to fetch open stops");
  }

  return allStops.filter((stop) => stop.openNow);
};
