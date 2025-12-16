import { create } from "zustand";
import { devtools } from "zustand/middleware";

/**
 * Zustand Store for Booking Management
 * Handles all booking-related state including tickets, transportation, and reservations
 */
const useBookingStore = create(
  devtools(
    (set, get) => ({
      // ========== State ==========
      bookings: [],
      activeBooking: null, // Currently active booking being created/edited
      isLoading: false,
      error: null,
      bookingHistory: [],

      // ========== Actions ==========

      /**
       * Set all bookings
       * @param {Array} bookings - Array of booking objects
       */
      setBookings: (bookings) =>
        set({ bookings, isLoading: false, error: null }),

      /**
       * Set loading state
       */
      setLoading: (isLoading) => set({ isLoading }),

      /**
       * Set error state
       */
      setError: (error) => set({ error, isLoading: false }),

      /**
       * Create a new booking
       * @param {Object} bookingData - Booking data to create
       */
      createBooking: (bookingData) => {
        const newBooking = {
          id: `BK${Date.now()}`,
          ...bookingData,
          status: "pending",
          createdAt: new Date().toISOString(),
        };

        set({
          bookings: [...get().bookings, newBooking],
          activeBooking: newBooking,
        });

        return newBooking;
      },

      /**
       * Update booking status
       * @param {string} bookingId - ID of the booking to update
       * @param {string} status - New status (pending, confirmed, cancelled)
       */
      updateBookingStatus: (bookingId, status) => {
        const bookings = get().bookings.map((booking) =>
          booking.id === bookingId
            ? { ...booking, status, updatedAt: new Date().toISOString() }
            : booking
        );
        set({ bookings });
      },

      /**
       * Confirm a booking
       * @param {string} bookingId - ID of the booking to confirm
       */
      confirmBooking: (bookingId) => {
        const bookings = get().bookings.map((booking) =>
          booking.id === bookingId
            ? {
                ...booking,
                status: "confirmed",
                confirmedAt: new Date().toISOString(),
              }
            : booking
        );
        set({ bookings, activeBooking: null });
      },

      /**
       * Cancel a booking
       * @param {string} bookingId - ID of the booking to cancel
       */
      cancelBooking: (bookingId) => {
        const bookings = get().bookings.map((booking) =>
          booking.id === bookingId
            ? {
                ...booking,
                status: "cancelled",
                cancelledAt: new Date().toISOString(),
              }
            : booking
        );

        // Move to history
        const cancelledBooking = bookings.find((b) => b.id === bookingId);
        if (cancelledBooking) {
          set({
            bookings: bookings.filter((b) => b.id !== bookingId),
            bookingHistory: [...get().bookingHistory, cancelledBooking],
          });
        }
      },

      /**
       * Get booking by ID
       * @param {string} bookingId - ID of the booking
       * @returns {Object|null} Booking object or null
       */
      getBookingById: (bookingId) => {
        return get().bookings.find((b) => b.id === bookingId) || null;
      },

      /**
       * Get bookings by stop ID
       * @param {string} stopId - ID of the stop
       * @returns {Array} Array of bookings for the stop
       */
      getBookingsByStopId: (stopId) => {
        return get().bookings.filter((b) => b.stopId === stopId);
      },

      /**
       * Get bookings by type
       * @param {string} bookingType - Type of booking (ticket, transportation, reservation)
       * @returns {Array} Array of bookings of the specified type
       */
      getBookingsByType: (bookingType) => {
        return get().bookings.filter((b) => b.bookingType === bookingType);
      },

      /**
       * Get confirmed bookings
       * @returns {Array} Array of confirmed bookings
       */
      getConfirmedBookings: () => {
        return get().bookings.filter((b) => b.status === "confirmed");
      },

      /**
       * Get pending bookings
       * @returns {Array} Array of pending bookings
       */
      getPendingBookings: () => {
        return get().bookings.filter((b) => b.status === "pending");
      },

      /**
       * Set active booking (for booking flow)
       * @param {Object} booking - Booking object
       */
      setActiveBooking: (booking) => set({ activeBooking: booking }),

      /**
       * Clear active booking
       */
      clearActiveBooking: () => set({ activeBooking: null }),

      /**
       * Clear all bookings
       */
      clearBookings: () =>
        set({ bookings: [], activeBooking: null, bookingHistory: [] }),

      /**
       * Get total booking cost
       * @returns {number} Total cost of all confirmed bookings
       */
      getTotalCost: () => {
        return get()
          .bookings.filter((b) => b.status === "confirmed")
          .reduce((total, booking) => {
            // Extract numeric value from price string (e.g., "150k VND" -> 150000)
            const priceMatch = booking.price?.match(/(\d+)k/);
            const price = priceMatch ? parseInt(priceMatch[1]) * 1000 : 0;
            return total + price;
          }, 0);
      },
    }),
    { name: "BookingStore" }
  )
);

export default useBookingStore;
