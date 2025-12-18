import React, { useState } from "react";
import { Card, Group, Text, Badge, Button, Box } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import {
  IconStar,
  IconMapPin,
  IconToolsKitchen2,
  IconCoffee,
  IconBed,
  IconBuildingChurch,
  IconCameraFilled,
  IconShoppingBag,
} from "@tabler/icons-react";
import {
  createItineraryAPI,
  fetchUserItinerariesAPI,
  fetchItineraryByIdAPI,
  optimizeItineraryAPI,
} from "../../apis/itineraryService";
import { addStopAPI } from "../../apis/stopService";
import { HARDCODED_TEST_USER } from "../../utils/constants";
import useItineraryStore from "../../stores/useItineraryStore";

// Category icon mapping
const getCategoryIcon = (category) => {
  const iconMap = {
    restaurant: IconToolsKitchen2,
    cafe: IconCoffee,
    hotel: IconBed,
    temple: IconBuildingChurch,
    attraction: IconCameraFilled,
    shopping: IconShoppingBag,
  };

  const IconComponent = iconMap[category?.toLowerCase()] || IconMapPin;
  return <IconComponent size={12} />;
};

/**
 * PlaceCard - Display place information extracted from AI response
 * @param {Object} place - Place object with name, category, rating, etc.
 * @param {Function} onAddToPlan - Callback when user clicks "Add to Plan"
 * @param {boolean} isAdded - Whether place is already in plan
 */
const PlaceCard = ({ place, onAddToPlan, isAdded = false }) => {
  const [isAdding, setIsAdding] = useState(false);

  // Access Zustand store to get current itinerary
  const { itineraryItems, setItinerary, currentItinerary } =
    useItineraryStore();

  const handleAddToItinerary = async () => {
    if (isAdded || isAdding) return;

    // Validate place object
    if (!place) {
      console.error("❌ No place object provided");
      notifications.show({
        title: "Error",
        message: "Invalid place data",
        color: "red",
      });
      return;
    }

    const placeId = place.place_id || place.id;

    if (!placeId || placeId === "undefined" || placeId === "null") {
      console.error("❌ Invalid or missing place_id:", {
        place,
        place_id: place.place_id,
        id: place.id,
      });
      notifications.show({
        title: "Error",
        message: "This place is missing a valid ID and cannot be added",
        color: "red",
      });
      return;
    }

    try {
      setIsAdding(true);

      let itineraryId = null;

      // Step 1: Check if user already has an itinerary
      try {
        const existingItineraries = await fetchUserItinerariesAPI(
          HARDCODED_TEST_USER.userId
        );

        if (existingItineraries && existingItineraries.length > 0) {
          // Use the first (most recent) itinerary
          itineraryId = existingItineraries[0].id;
          console.log("✅ Using existing itinerary:", itineraryId);
        }
      } catch (error) {
        console.log("No existing itinerary found, will create new one");
      }

      // Step 2: If no itinerary exists, create one
      if (!itineraryId) {
        const today = new Date();
        const startDate = today.toISOString().split("T")[0];
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        const endDate = tomorrow.toISOString().split("T")[0];

        const itineraryResponse = await createItineraryAPI(
          {
            title: `My Da Nang Trip`,
            startDate,
            endDate,
            totalBudget: 0,
            currency: "VND",
          },
          HARDCODED_TEST_USER.userId
        );

        itineraryId = itineraryResponse?.itinerary?.id;

        if (!itineraryId) {
          throw new Error("Failed to create itinerary");
        }

        console.log("✅ Created new itinerary:", itineraryId);
      }

      // Step 3: Calculate order_index based on existing stops in Day 1
      let orderIndex = 1;
      if (itineraryItems && itineraryItems[0]?.stops) {
        orderIndex = itineraryItems[0].stops.length + 1;
      }

      // Step 4: Prepare stop data for backend
      const stopData = {
        place_id: place.place_id || place.id,
        day_index: 1, // Add to Day 1 (1-indexed for backend)
        order_index: orderIndex, // Sequential order (1-indexed for backend)
        arrival_time: null, // Will be optimized later
        stay_minutes: 60,
        notes: "",
        tags: place.tags || [],
        snapshot: {
          name: place.name,
          category: place.category || place.type,
          address: place.address,
          rating: place.rating,
          image: place.image,
          lat: place.lat,
          lng: place.lng,
        },
      };

      // DEBUG: Log complete place object and stopData
      console.log("🔍 PLACE OBJECT:", JSON.stringify(place, null, 2));
      console.log("🔍 STOP DATA TO SEND:", JSON.stringify(stopData, null, 2));

      console.log("🔍 Adding stop to itinerary:", {
        itineraryId,
        stopData,
      });

      // Step 5: Add stop to itinerary using stopService
      const stopResponse = await addStopAPI(
        itineraryId,
        stopData,
        HARDCODED_TEST_USER.userId
      );

      console.log("✅ Stop added successfully:", stopResponse);

      // Step 6: Refresh itinerary to update UI immediately
      try {
        const updatedItinerary = await fetchItineraryByIdAPI(
          itineraryId,
          HARDCODED_TEST_USER.userId
        );
        if (updatedItinerary?.days) {
          setItinerary(updatedItinerary.days);
          console.log("✅ Itinerary refreshed, UI updated");
        }
      } catch (refreshError) {
        console.warn("Failed to refresh itinerary:", refreshError);
      }

      // Step 7: Optional - Try to optimize the itinerary route
      try {
        await optimizeItineraryAPI(itineraryId, 1);
        console.log("✅ Itinerary route optimized");
      } catch (optimizeError) {
        console.warn(
          "Optimization failed, but itinerary was created:",
          optimizeError
        );
      }

      // Show success notification
      notifications.show({
        title: "Added to Itinerary",
        message: `${place.name} has been added to your trip!`,
        color: "green",
        icon: "✓",
      });

      // Call parent callback
      if (onAddToPlan) {
        onAddToPlan(place);
      }
    } catch (error) {
      console.error("❌ Error adding to itinerary:", error);
      console.error("❌ Error message:", error.message);
      console.error("❌ Error response:", error.response);
      console.error("❌ Error data:", error.response?.data);
      console.error("❌ Error status:", error.response?.status);
      console.error("❌ Request config:", error.config);
      console.error("❌ Request data:", error.config?.data);

      // If detail is an array, log each validation error
      if (Array.isArray(error.response?.data?.detail)) {
        console.error("Validation errors:");
        error.response.data.detail.forEach((err, index) => {
          console.error(`  ${index + 1}.`, JSON.stringify(err, null, 2));
        });
      }

      // Format error message for display
      let errorMessage = "Failed to add place to itinerary";

      if (Array.isArray(error.response?.data?.detail)) {
        // Join all validation error messages
        errorMessage = error.response.data.detail
          .map((err) => err.msg || err.message || JSON.stringify(err))
          .join(", ");
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }

      notifications.show({
        title: "Error",
        message: errorMessage,
        color: "red",
      });
    } finally {
      setIsAdding(false);
    }
  };

  return (
    <Card
      shadow="sm"
      padding="md"
      radius="md"
      withBorder
      style={{
        transition: "all 0.2s",
        cursor: "pointer",
      }}
      styles={{
        root: {
          "&:hover": {
            boxShadow: "var(--mantine-shadow-md)",
            transform: "translateY(-2px)",
          },
        },
      }}
    >
      <Group justify="space-between" align="flex-start" wrap="nowrap">
        <Box flex={1}>
          <Text fw={600} size="sm" lineClamp={1}>
            {place.name}
          </Text>

          <Group gap="xs" mt={4}>
            {place.category && (
              <Badge
                size="xs"
                variant="light"
                color="gray"
                leftSection={getCategoryIcon(place.category)}
              >
                {place.category}
              </Badge>
            )}

            {place.rating && (
              <Group gap={4}>
                <IconStar size={14} fill="gold" color="gold" />
                <Text size="xs" c="dimmed" fw={500}>
                  {place.rating}
                </Text>
              </Group>
            )}
          </Group>

          {place.address && (
            <Text size="xs" c="dimmed" mt={4} lineClamp={1}>
              {place.address}
            </Text>
          )}

          {!place.address && place.distance_km && (
            <Text size="xs" c="dimmed" mt={4}>
              {place.distance_km.toFixed(2)} km away
            </Text>
          )}
        </Box>

        <Button
          size="xs"
          variant={isAdded ? "light" : "filled"}
          color={isAdded ? "green" : "dark"}
          onClick={handleAddToItinerary}
          disabled={isAdded}
          loading={isAdding}
          styles={{
            root: {
              minWidth: 80,
            },
          }}
        >
          {isAdded ? "✓ Added" : "+ Add"}
        </Button>
      </Group>
    </Card>
  );
};

export default PlaceCard;
