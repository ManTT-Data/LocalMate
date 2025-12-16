/**
 * Example Usage of Zustand Stores and Mock APIs
 * This file demonstrates how to use the newly created stores and APIs
 */

import React, { useEffect } from "react";

// Import stores
import useBookingStore from "../stores/useBookingStore";
import useUserStore from "../stores/useUserStore";
import useStopStore from "../stores/useStopStore";

// Import API services
import {
  fetchUserBookingsAPI,
  createBookingAPI,
  confirmBookingAPI,
} from "../apis/bookingService";
import {
  fetchUserProfileAPI,
  fetchUserPreferencesAPI,
  updateUserLocationAPI,
} from "../apis/userService";
import { fetchAllStopsAPI, fetchNearbyStopsAPI } from "../apis/stopService";

/**
 * Example Component: BookingManager
 * Demonstrates booking store and API usage
 */
export const BookingManagerExample = () => {
  const {
    bookings,
    setBookings,
    createBooking,
    confirmBooking,
    getConfirmedBookings,
  } = useBookingStore();

  useEffect(() => {
    // Fetch user bookings on mount
    const loadBookings = async () => {
      try {
        const userBookings = await fetchUserBookingsAPI("user-001");
        setBookings(userBookings);
        console.log("✅ Bookings loaded:", userBookings);
      } catch (error) {
        console.error("❌ Error loading bookings:", error);
      }
    };

    loadBookings();
  }, [setBookings]);

  const handleCreateBooking = async () => {
    try {
      // Create booking in local store first
      const newBooking = createBooking({
        userId: "user-001",
        stopId: "marble-mountains",
        bookingType: "ticket",
        serviceName: "Entry Ticket",
        price: "40k VND",
        bookingDetails: {
          quantity: 1,
          date: "2024-10-24",
          time: "09:00 AM",
        },
      });

      console.log("📝 Local booking created:", newBooking);

      // Sync with backend API
      const result = await createBookingAPI(newBooking);
      console.log("✅ Booking synced with backend:", result);

      // Confirm booking
      if (result.success) {
        await confirmBookingAPI(newBooking.id);
        confirmBooking(newBooking.id);
        console.log("✅ Booking confirmed");
      }
    } catch (error) {
      console.error("❌ Error creating booking:", error);
    }
  };

  return (
    <div>
      <h2>Booking Manager Example</h2>
      <button onClick={handleCreateBooking}>Create Test Booking</button>
      <div>
        <p>Total Bookings: {bookings.length}</p>
        <p>Confirmed Bookings: {getConfirmedBookings().length}</p>
      </div>
    </div>
  );
};

/**
 * Example Component: UserProfile
 * Demonstrates user store and API usage
 */
export const UserProfileExample = () => {
  const {
    user,
    preferences,
    setUser,
    setPreferences,
    updateLocation,
    addRecentSearch,
  } = useUserStore();

  useEffect(() => {
    // Load user profile and preferences
    const loadUserData = async () => {
      try {
        const profile = await fetchUserProfileAPI("user-001");
        setUser(profile);
        console.log("✅ User profile loaded:", profile);

        const prefs = await fetchUserPreferencesAPI("user-001");
        setPreferences(prefs);
        console.log("✅ User preferences loaded:", prefs);
      } catch (error) {
        console.error("❌ Error loading user data:", error);
      }
    };

    loadUserData();
  }, [setUser, setPreferences]);

  const handleUpdateLocation = async () => {
    try {
      const newLocation = { lat: 16.0544, lng: 108.2022 };

      // Update in backend
      await updateUserLocationAPI("user-001", newLocation);

      // Update in store
      updateLocation(newLocation);
      console.log("✅ Location updated:", newLocation);
    } catch (error) {
      console.error("❌ Error updating location:", error);
    }
  };

  const handleAddSearch = () => {
    addRecentSearch("Dragon Bridge");
    console.log("✅ Added to recent searches");
  };

  return (
    <div>
      <h2>User Profile Example</h2>
      {user && (
        <div>
          <p>Name: {user.name}</p>
          <p>
            Location: {user.location?.lat}, {user.location?.lng}
          </p>
          <p>Recent Searches: {preferences?.recentSearches?.join(", ")}</p>
        </div>
      )}
      <button onClick={handleUpdateLocation}>Update Location</button>
      <button onClick={handleAddSearch}>Add Recent Search</button>
    </div>
  );
};

/**
 * Example Component: StopExplorer
 * Demonstrates stop store and API usage
 */
export const StopExplorerExample = () => {
  const {
    stops,
    setStops,
    activeStop,
    setActiveStop,
    getTopRatedStops,
    searchStops,
  } = useStopStore();

  useEffect(() => {
    // Load all stops
    const loadStops = async () => {
      try {
        const allStops = await fetchAllStopsAPI();
        setStops(allStops);
        console.log("✅ Stops loaded:", allStops);
      } catch (error) {
        console.error("❌ Error loading stops:", error);
      }
    };

    loadStops();
  }, [setStops]);

  const handleFetchNearby = async () => {
    try {
      // Fetch stops near Da Nang center
      const nearbyStops = await fetchNearbyStopsAPI(16.0544, 108.2022, 5);
      console.log("✅ Nearby stops:", nearbyStops);
    } catch (error) {
      console.error("❌ Error fetching nearby stops:", error);
    }
  };

  const handleSearch = () => {
    const results = searchStops("beach");
    console.log("🔍 Search results for 'beach':", results);
  };

  const handleSelectStop = (stopId) => {
    setActiveStop(stopId);
    console.log("✅ Active stop set:", stopId);
  };

  return (
    <div>
      <h2>Stop Explorer Example</h2>
      <div>
        <p>Total Stops: {stops.length}</p>
        <p>Top Rated Stops: {getTopRatedStops(5).length}</p>
        {activeStop && <p>Active Stop: {activeStop.name}</p>}
      </div>
      <button onClick={handleFetchNearby}>Fetch Nearby Stops</button>
      <button onClick={handleSearch}>Search "beach"</button>
      <button onClick={() => handleSelectStop("marble-mountains")}>
        Select Marble Mountains
      </button>
    </div>
  );
};

/**
 * Complete Example: Integration Demo
 * Shows how all stores can work together
 */
export const IntegrationDemo = () => {
  const user = useUserStore((state) => state.user);
  const bookings = useBookingStore((state) => state.bookings);
  const stops = useStopStore((state) => state.stops);

  const demoCompleteFlow = async () => {
    console.log("🚀 Starting integration demo...");

    try {
      // 1. Load user profile
      const profile = await fetchUserProfileAPI("user-001");
      useUserStore.getState().setUser(profile);
      console.log("1️⃣ User loaded");

      // 2. Load available stops
      const allStops = await fetchAllStopsAPI();
      useStopStore.getState().setStops(allStops);
      console.log("2️⃣ Stops loaded");

      // 3. Find nearby stops based on user location
      if (profile.location) {
        const nearby = await fetchNearbyStopsAPI(
          profile.location.lat,
          profile.location.lng,
          10
        );
        console.log("3️⃣ Nearby stops found:", nearby.length);
      }

      // 4. Create a booking for a stop
      const booking = useBookingStore.getState().createBooking({
        userId: "user-001",
        stopId: "marble-mountains",
        bookingType: "ticket",
        serviceName: "Entry Ticket",
        price: "40k VND",
      });
      console.log("4️⃣ Booking created:", booking.id);

      // 5. Add to recent searches
      useUserStore.getState().addRecentSearch("Marble Mountains");
      console.log("5️⃣ Added to recent searches");

      console.log("✅ Integration demo completed successfully!");
    } catch (error) {
      console.error("❌ Integration demo failed:", error);
    }
  };

  return (
    <div>
      <h2>Integration Demo</h2>
      <div>
        <p>User: {user?.name || "Not loaded"}</p>
        <p>Bookings: {bookings?.length || 0}</p>
        <p>Available Stops: {stops?.length || 0}</p>
      </div>
      <button onClick={demoCompleteFlow}>Run Complete Demo</button>
    </div>
  );
};

// Export all examples
export default {
  BookingManagerExample,
  UserProfileExample,
  StopExplorerExample,
  IntegrationDemo,
};
