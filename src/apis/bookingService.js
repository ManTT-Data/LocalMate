/**
 * Mock Backend Service for Booking Management
 * Simulates API calls for bookings with delays and occasional failures
 */

import { mockBookings } from "../data/mockData";

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
 * Fetch all bookings for a user
 * @param {string} userId - User ID
 * @returns {Promise<Array>} User's bookings
 */
export const fetchUserBookingsAPI = async (userId) => {
  await simulateDelay();

  if (shouldFail()) {
    throw new Error("Failed to fetch bookings");
  }

  // Filter bookings by user ID
  return mockBookings.filter((booking) => booking.userId === userId);
};

/**
 * Fetch booking by ID
 * @param {string} bookingId - Booking ID
 * @returns {Promise<Object>} Booking object
 */
export const fetchBookingByIdAPI = async (bookingId) => {
  await simulateDelay(300, 800);

  if (shouldFail()) {
    throw new Error("Failed to fetch booking details");
  }

  const booking = mockBookings.find((b) => b.id === bookingId);

  if (!booking) {
    throw new Error("Booking not found");
  }

  return booking;
};

/**
 * Create a new booking
 * @param {Object} bookingData - Booking data
 * @returns {Promise<Object>} Created booking
 */
export const createBookingAPI = async (bookingData) => {
  await simulateDelay(800, 2000);

  if (shouldFail()) {
    throw new Error("Failed to create booking. Please try again.");
  }

  const newBooking = {
    id: `BK${Date.now()}`,
    ...bookingData,
    status: "pending",
    createdAt: new Date().toISOString(),
  };

  return {
    success: true,
    booking: newBooking,
    message: "Booking created successfully",
  };
};

/**
 * Confirm a booking
 * @param {string} bookingId - Booking ID
 * @returns {Promise<Object>} Confirmation result
 */
export const confirmBookingAPI = async (bookingId) => {
  await simulateDelay(500, 1200);

  if (shouldFail()) {
    throw new Error("Failed to confirm booking");
  }

  return {
    success: true,
    bookingId,
    status: "confirmed",
    confirmedAt: new Date().toISOString(),
    message: "Booking confirmed successfully",
  };
};

/**
 * Cancel a booking
 * @param {string} bookingId - Booking ID
 * @returns {Promise<Object>} Cancellation result
 */
export const cancelBookingAPI = async (bookingId) => {
  await simulateDelay(500, 1000);

  if (shouldFail()) {
    throw new Error("Failed to cancel booking");
  }

  return {
    success: true,
    bookingId,
    status: "cancelled",
    cancelledAt: new Date().toISOString(),
    refundAmount: null, // Could calculate refund based on cancellation policy
    message: "Booking cancelled successfully",
  };
};

/**
 * Update booking details
 * @param {string} bookingId - Booking ID
 * @param {Object} updates - Fields to update
 * @returns {Promise<Object>} Update result
 */
export const updateBookingAPI = async (bookingId, updates) => {
  await simulateDelay(400, 900);

  if (shouldFail()) {
    throw new Error("Failed to update booking");
  }

  return {
    success: true,
    bookingId,
    updates,
    updatedAt: new Date().toISOString(),
    message: "Booking updated successfully",
  };
};

/**
 * Get bookings by stop ID
 * @param {string} stopId - Stop ID
 * @returns {Promise<Array>} Bookings for the stop
 */
export const fetchBookingsByStopIdAPI = async (stopId) => {
  await simulateDelay(300, 700);

  if (shouldFail()) {
    throw new Error("Failed to fetch stop bookings");
  }

  return mockBookings.filter((booking) => booking.stopId === stopId);
};

/**
 * Get bookings by type
 * @param {string} userId - User ID
 * @param {string} bookingType - Booking type (ticket, transportation, reservation)
 * @returns {Promise<Array>} Bookings of the specified type
 */
export const fetchBookingsByTypeAPI = async (userId, bookingType) => {
  await simulateDelay(300, 700);

  if (shouldFail()) {
    throw new Error("Failed to fetch bookings by type");
  }

  return mockBookings.filter(
    (booking) =>
      booking.userId === userId && booking.bookingType === bookingType
  );
};

/**
 * Get booking statistics for user
 * @param {string} userId - User ID
 * @returns {Promise<Object>} Booking statistics
 */
export const fetchBookingStatsAPI = async (userId) => {
  await simulateDelay(400, 800);

  if (shouldFail()) {
    throw new Error("Failed to fetch booking statistics");
  }

  const userBookings = mockBookings.filter((b) => b.userId === userId);

  const stats = {
    total: userBookings.length,
    confirmed: userBookings.filter((b) => b.status === "confirmed").length,
    pending: userBookings.filter((b) => b.status === "pending").length,
    cancelled: userBookings.filter((b) => b.status === "cancelled").length,
    byType: {
      ticket: userBookings.filter((b) => b.bookingType === "ticket").length,
      transportation: userBookings.filter(
        (b) => b.bookingType === "transportation"
      ).length,
      reservation: userBookings.filter((b) => b.bookingType === "reservation")
        .length,
    },
    totalSpent: userBookings
      .filter((b) => b.status === "confirmed" && b.price)
      .reduce((sum, b) => {
        const match = b.price.match(/(\d+)k/);
        return sum + (match ? parseInt(match[1]) * 1000 : 0);
      }, 0),
  };

  return stats;
};
