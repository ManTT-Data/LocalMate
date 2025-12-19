import React, { useState } from "react";
import { Card, Group, Text, Badge, Button, Box, Image, ActionIcon, Tooltip } from "@mantine/core";
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
  IconHeart,
  IconShare,
  IconNavigation,
  IconPlus,
  IconCheck,
} from "@tabler/icons-react";
import {
  createItineraryAPI,
  fetchUserItinerariesAPI,
  fetchItineraryByIdAPI,
  optimizeItineraryAPI,
} from "../../apis/itineraryService";
import { addStopAPI } from "../../apis/stopService";
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

// Category color mapping
const getCategoryColor = (category) => {
  const colorMap = {
    restaurant: "#FF6B6B",
    cafe: "#A0522D",
    hotel: "#9B5DE5",
    temple: "#FFD93D",
    attraction: "#00BBF9",
    shopping: "#6BCB77",
  };
  return colorMap[category?.toLowerCase()] || "#00bfa6";
};

/**
 * PlaceCard - Display place information extracted from AI response
 * @param {Object} place - Place object with name, category, rating, etc.
 * @param {Function} onAddToPlan - Callback when user clicks "Add to Plan"
 * @param {boolean} isAdded - Whether place is already in plan
 */
const PlaceCard = ({ place, onAddToPlan, isAdded = false }) => {
  const [isAdding, setIsAdding] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [isSaved, setIsSaved] = useState(false);

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
        const existingItineraries = await fetchUserItinerariesAPI();

        if (existingItineraries && existingItineraries.length > 0) {
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

        const itineraryResponse = await createItineraryAPI({
          title: `My Da Nang Trip`,
          startDate,
          endDate,
          totalBudget: 0,
          currency: "VND",
        });

        itineraryId = itineraryResponse?.itinerary?.id;

        if (!itineraryId) {
          throw new Error("Failed to create itinerary");
        }

        console.log("✅ Created new itinerary:", itineraryId);
      }

      // Step 3: Calculate order_index based on existing stops
      let orderIndex = 1;
      if (itineraryItems && itineraryItems[0]?.stops) {
        orderIndex = itineraryItems[0].stops.length + 1;
      }

      // Step 4: Prepare stop data
      const stopData = {
        place_id: place.place_id || place.id,
        day_index: 1,
        order_index: orderIndex,
        arrival_time: null,
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

      // Step 5: Add stop to itinerary
      const stopResponse = await addStopAPI(itineraryId, stopData);
      console.log("✅ Stop added successfully:", stopResponse);

      // Step 6: Refresh itinerary
      try {
        const updatedItinerary = await fetchItineraryByIdAPI(itineraryId);
        if (updatedItinerary?.days) {
          setItinerary(updatedItinerary.days);
        }
      } catch (refreshError) {
        console.warn("Failed to refresh itinerary:", refreshError);
      }

      // Step 7: Optional optimization
      try {
        await optimizeItineraryAPI(itineraryId, 1);
      } catch (optimizeError) {
        console.warn("Optimization failed:", optimizeError);
      }

      notifications.show({
        title: "Added to Itinerary",
        message: `${place.name} has been added to your trip!`,
        color: "green",
        icon: "✓",
      });

      if (onAddToPlan) {
        onAddToPlan(place);
      }
    } catch (error) {
      console.error("❌ Error adding to itinerary:", error);

      let errorMessage = "Failed to add place to itinerary";
      if (Array.isArray(error.response?.data?.detail)) {
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

  const handleSave = (e) => {
    e.stopPropagation();
    setIsSaved(!isSaved);
    notifications.show({
      title: isSaved ? "Removed from saved" : "Saved!",
      message: isSaved ? `${place.name} removed from favorites` : `${place.name} added to favorites`,
      color: isSaved ? "gray" : "pink",
    });
  };

  const handleShare = (e) => {
    e.stopPropagation();
    navigator.clipboard.writeText(`Check out ${place.name}!`);
    notifications.show({
      title: "Copied!",
      message: "Link copied to clipboard",
      color: "teal",
    });
  };

  const handleNavigate = (e) => {
    e.stopPropagation();
    if (place.lat && place.lng) {
      window.open(`https://www.google.com/maps/dir/?api=1&destination=${place.lat},${place.lng}`, "_blank");
    }
  };

  const categoryColor = getCategoryColor(place.category);

  return (
    <Card
      shadow="sm"
      padding={0}
      radius="lg"
      withBorder
      className="place-card"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        overflow: "hidden",
        transition: "all 0.3s ease",
        transform: isHovered ? "translateY(-4px)" : "translateY(0)",
        boxShadow: isHovered
          ? "0 20px 40px -15px rgba(0, 0, 0, 0.2)"
          : "0 2px 8px rgba(0, 0, 0, 0.08)",
      }}
    >
      {/* Image Section with Overlay */}
      {place.image && (
        <Box pos="relative" style={{ height: 140, overflow: "hidden" }}>
          <Image
            src={place.image}
            alt={place.name}
            height={140}
            fit="cover"
            className="place-card-image"
            style={{
              transition: "transform 0.5s ease",
              transform: isHovered ? "scale(1.08)" : "scale(1)",
            }}
          />

          {/* Gradient Overlay */}
          <Box
            pos="absolute"
            top={0}
            left={0}
            right={0}
            bottom={0}
            style={{
              background: "linear-gradient(to top, rgba(0,0,0,0.6) 0%, transparent 60%)",
              opacity: isHovered ? 1 : 0.5,
              transition: "opacity 0.3s ease",
            }}
          />

          {/* Quick Action Buttons */}
          <Group
            pos="absolute"
            top={8}
            right={8}
            gap={4}
            style={{
              opacity: isHovered ? 1 : 0,
              transform: isHovered ? "translateY(0)" : "translateY(-10px)",
              transition: "all 0.3s ease",
            }}
          >
            <Tooltip label="Save" withArrow>
              <ActionIcon
                variant="filled"
                color={isSaved ? "pink" : "dark"}
                radius="xl"
                size="sm"
                onClick={handleSave}
                style={{
                  background: isSaved ? "#FF6B6B" : "rgba(255,255,255,0.9)",
                  color: isSaved ? "white" : "#333",
                }}
              >
                <IconHeart size={14} fill={isSaved ? "currentColor" : "none"} />
              </ActionIcon>
            </Tooltip>
            <Tooltip label="Share" withArrow>
              <ActionIcon
                variant="filled"
                radius="xl"
                size="sm"
                onClick={handleShare}
                style={{ background: "rgba(255,255,255,0.9)", color: "#333" }}
              >
                <IconShare size={14} />
              </ActionIcon>
            </Tooltip>
            {place.lat && place.lng && (
              <Tooltip label="Navigate" withArrow>
                <ActionIcon
                  variant="filled"
                  radius="xl"
                  size="sm"
                  onClick={handleNavigate}
                  style={{ background: "rgba(255,255,255,0.9)", color: "#333" }}
                >
                  <IconNavigation size={14} />
                </ActionIcon>
              </Tooltip>
            )}
          </Group>

          {/* Rating Badge */}
          {place.rating && (
            <Badge
              pos="absolute"
              bottom={8}
              left={8}
              variant="filled"
              color="dark"
              size="sm"
              leftSection={<IconStar size={12} fill="gold" color="gold" />}
              style={{
                background: "rgba(0,0,0,0.7)",
                backdropFilter: "blur(4px)",
              }}
            >
              {place.rating}
            </Badge>
          )}

          {/* Category Accent */}
          <Box
            pos="absolute"
            bottom={0}
            left={0}
            right={0}
            h={3}
            style={{ background: categoryColor }}
          />
        </Box>
      )}

      {/* Content Section */}
      <Box p="sm">
        <Group justify="space-between" align="flex-start" wrap="nowrap" gap="xs">
          <Box flex={1} style={{ minWidth: 0 }}>
            <Text fw={600} size="sm" lineClamp={1}>
              {place.name}
            </Text>

            <Group gap={6} mt={4}>
              {place.category && (
                <Badge
                  size="xs"
                  variant="light"
                  color="gray"
                  leftSection={getCategoryIcon(place.category)}
                  style={{
                    borderLeft: `2px solid ${categoryColor}`,
                  }}
                >
                  {place.category}
                </Badge>
              )}

              {!place.image && place.rating && (
                <Group gap={4}>
                  <IconStar size={12} fill="gold" color="gold" />
                  <Text size="xs" c="dimmed" fw={500}>
                    {place.rating}
                  </Text>
                </Group>
              )}

              {place.distance_km && (
                <Text size="xs" c="dimmed">
                  {place.distance_km.toFixed(1)} km
                </Text>
              )}
            </Group>

            {place.address && (
              <Text size="xs" c="dimmed" mt={4} lineClamp={1}>
                {place.address}
              </Text>
            )}
          </Box>

          <Button
            size="xs"
            variant={isAdded ? "light" : "filled"}
            color={isAdded ? "green" : "teal"}
            onClick={handleAddToItinerary}
            disabled={isAdded}
            loading={isAdding}
            radius="xl"
            leftSection={isAdded ? <IconCheck size={14} /> : <IconPlus size={14} />}
            style={{
              transition: "all 0.2s ease",
              boxShadow: isAdded ? "none" : "0 4px 12px rgba(0, 191, 166, 0.3)",
            }}
          >
            {isAdded ? "Added" : "Add"}
          </Button>
        </Group>
      </Box>
    </Card>
  );
};

export default PlaceCard;
