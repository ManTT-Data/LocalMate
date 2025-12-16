/**
 * Mock Backend Service for Itinerary Management
 * Simulates API calls with delays and occasional failures
 */

import { destinations } from "../data/mockData";

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
 * Fetch itinerary data from "backend"
 * @returns {Promise<Array>} Itinerary items
 */
export const fetchItineraryFromBackend = async () => {
  await simulateDelay();

  if (shouldFail()) {
    throw new Error("Failed to fetch itinerary data");
  }

  // Return mock itinerary data with Day 2 complete
  return [
    {
      day: 1,
      title: "Cultural Exploration",
      date: "Oct 24",
      totalCost: "1.2m VND",
      totalTime: "45 mins",
      stops: [
        {
          id: "start-day1",
          time: "08:30 AM",
          type: "start",
          name: "Start from Hotel",
          locationName: "Hyatt Regency Danang",
          location: { lat: 16.012855984, lng: 108.263785 },
          isBooked: false,
          nextTravel: {
            type: "drive",
            duration: "10 min",
            mode: "taxi",
            label: "Book Grab",
            price: "20k VND",
            bookable: true,
          },
        },
        {
          id: "marble-mountains",
          time: "09:00 AM",
          type: "destination",
          destinationId: "marble-mountains",
          destination: destinations[0],
          isBooked: false,
          bookingDetails: {
            type: "ticket",
            price: "40k VND",
            bookable: true,
          },
          nextTravel: {
            type: "drive",
            duration: "20 min",
            mode: "taxi",
            label: "Book Grab",
            price: "150k VND",
            bookable: true,
          },
        },
        {
          id: "lunch-mi-quang",
          time: "11:00 AM",
          type: "destination",
          destinationId: "mi-quang-ba-mua",
          destination: destinations[1],
          isTopPick: true,
          isBooked: false,
          bookingDetails: {
            type: "reservation",
            bookable: false,
          },
        },
      ],
    },
    {
      day: 2,
      title: "Beach & Relaxation",
      date: "Oct 25",
      totalCost: "800k VND",
      totalTime: "6 hrs",
      stops: [
        {
          id: "start-day2",
          time: "09:00 AM",
          type: "start",
          name: "Start from Hotel",
          locationName: "Hyatt Regency Danang",
          location: { lat: 16.012855984, lng: 108.263785 },
          isBooked: false,
          nextTravel: {
            type: "drive",
            duration: "20 min",
            mode: "taxi",
            label: "Book Grab",
            price: "10k VND",
            bookable: true,
          },
        },
        {
          id: "my-khe-beach",
          time: "09:30 AM",
          type: "destination",
          destinationId: "my-khe-beach",
          destination: {
            id: "my-khe-beach",
            name: "My Khe Beach",
            description: "One of the most beautiful beaches in Vietnam",
            image:
              "https://lh3.googleusercontent.com/aida-public/AB6AXuCWqXzVxKzOH9kOBKW4_h5F5j8hNqGdX3jX1f5K5j8hNqGdX3jX1f5K5j8",
            location: { lat: 16.0397, lng: 108.2372 },
            rating: 4.7,
            reviews: 3200,
            type: "Beach",
            duration: "3 hrs",
            openNow: true,
            entryFee: "Free",
          },
          isBooked: false,
          nextTravel: {
            type: "drive",
            duration: "10 min",
            mode: "taxi",
            label: "Book Grab",
            price: "100k VND",
            bookable: true,
          },
        },
        {
          id: "seafood-lunch",
          time: "12:30 PM",
          type: "destination",
          destinationId: "be-man-seafood",
          destination: {
            id: "be-man-seafood",
            name: "Bé Mặn Seafood",
            description: "Fresh seafood by the beach",
            image:
              "https://lh3.googleusercontent.com/aida-public/AB6AXuBPzVxKzOH9kOBKW4_h5F5j8hNqGdX3jX1f5K5j8hNqGdX3jX1f5K5j8",
            location: { lat: 16.0421, lng: 108.2401 },
            rating: 4.5,
            reviews: 1800,
            type: "Restaurant",
            duration: "1.5 hrs",
            openNow: true,
            isTopPick: true,
          },
          isTopPick: true,
          isBooked: false,
          bookingDetails: {
            type: "reservation",
            bookable: false,
          },
        },
      ],
    },
  ];
};

/**
 * Book a service (Grab, ticket, reservation)
 * @param {string} stopId - ID of the stop
 * @param {string} serviceType - Type of service (grab, ticket, reservation)
 * @param {Object} details - Booking details
 * @returns {Promise<Object>} Booking confirmation
 */
export const bookServiceAPI = async (stopId, serviceType, details = {}) => {
  await simulateDelay(800, 2000);

  if (shouldFail()) {
    throw new Error(`Failed to book ${serviceType}. Please try again.`);
  }

  // Return booking confirmation
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
 * Save itinerary changes to backend
 * @param {Array} itineraryData - Updated itinerary data
 * @returns {Promise<Object>} Save confirmation
 */
export const updateItineraryAPI = async (itineraryData) => {
  await simulateDelay(300, 800);

  if (shouldFail()) {
    throw new Error("Failed to save itinerary changes");
  }

  return {
    success: true,
    savedAt: new Date().toISOString(),
    message: "Itinerary updated successfully",
  };
};

/**
 * Cancel a booking
 * @param {string} bookingId - Booking ID to cancel
 * @returns {Promise<Object>} Cancellation confirmation
 */
export const cancelBookingAPI = async (bookingId) => {
  await simulateDelay();

  if (shouldFail()) {
    throw new Error("Failed to cancel booking");
  }

  return {
    success: true,
    bookingId,
    cancelledAt: new Date().toISOString(),
    message: "Booking cancelled successfully",
  };
};
