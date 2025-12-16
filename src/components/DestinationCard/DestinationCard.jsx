import React, { useState } from "react";
import {
  Paper,
  Box,
  Group,
  Text,
  Badge,
  Anchor,
  Divider,
  ActionIcon,
  Collapse,
  Button,
} from "@mantine/core";
import {
  IconClock,
  IconTicket,
  IconCamera,
  IconChevronUp,
  IconChevronDown,
  IconX,
  IconPlus,
  IconCheck,
} from "@tabler/icons-react";
import { destinations } from "../../data/mockData";
import useItineraryStore from "../../stores/useItineraryStore";

const DestinationCard = ({ destination = destinations[0], onClose }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const { itineraryItems, addDestinationToItinerary } = useItineraryStore();

  // Check if this destination is already in the itinerary (any day)
  const isInItinerary = itineraryItems.some((day) =>
    day.stops?.some((stop) => stop.destinationId === destination.id)
  );

  console.log("DestinationCard render - itineraryItems:", itineraryItems);
  console.log("DestinationCard render - destination.id:", destination.id);
  console.log("DestinationCard render - isInItinerary:", isInItinerary);

  const handleAddToItinerary = () => {
    console.log("handleAddToItinerary called");
    console.log("isInItinerary:", isInItinerary);
    console.log("destination:", destination);
    console.log(
      "addDestinationToItinerary function:",
      addDestinationToItinerary
    );

    if (!isInItinerary) {
      console.log("Adding destination to itinerary...");
      // Add to Day 1 (index 0) by default
      addDestinationToItinerary(0, destination);
      console.log("Destination added!");
    } else {
      console.log("Destination already in itinerary, skipping");
    }
  };

  return (
    <Paper
      p="md"
      radius="xl"
      shadow="xl"
      withBorder
      style={{
        pointerEvents: "auto",
        transition: "all 0.3s",
        position: "relative",
      }}
      styles={{
        root: {
          "&:hover": {
            boxShadow: "var(--mantine-shadow-xl)",
          },
        },
      }}
    >
      {/* Controls */}
      <Group
        gap={6}
        style={{
          position: "absolute",
          top: "0.5rem",
          right: "0.5rem",
          zIndex: 20,
        }}
      >
        <ActionIcon
          variant={isCollapsed ? "light" : "filled"}
          color={isCollapsed ? "gray" : "dark"}
          size="sm"
          radius="xl"
          onClick={(e) => {
            e.stopPropagation();
            setIsCollapsed(!isCollapsed);
          }}
          style={
            !isCollapsed
              ? {
                  backgroundColor: "rgba(0, 0, 0, 0.5)",
                  backdropFilter: "blur(4px)",
                }
              : {}
          }
        >
          {isCollapsed ? (
            <IconChevronDown size={14} />
          ) : (
            <IconChevronUp size={14} />
          )}
        </ActionIcon>
        <ActionIcon
          variant={isCollapsed ? "light" : "filled"}
          color="red"
          size="sm"
          radius="xl"
          onClick={(e) => {
            e.stopPropagation();
            onClose && onClose();
          }}
          style={
            !isCollapsed
              ? {
                  backgroundColor: "rgba(0, 0, 0, 0.5)",
                  backdropFilter: "blur(4px)",
                  color: "#ff6b6b",
                }
              : {}
          }
        >
          <IconX size={14} />
        </ActionIcon>
      </Group>

      {/* Image */}
      <Box
        h={isCollapsed ? 0 : 128}
        style={{
          borderRadius: "var(--mantine-radius-lg)",
          backgroundImage: `url("${destination.image}")`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          position: "relative",
          overflow: "hidden",
          transition: "height 0.3s ease",
          opacity: isCollapsed ? 0 : 1,
        }}
      >
        <Badge
          variant="filled"
          color="dark"
          size="sm"
          radius="md"
          leftSection={<IconCamera size={12} />}
          style={{
            position: "absolute",
            top: "0.5rem",
            left: "0.5rem",
            backdropFilter: "blur(8px)",
          }}
        >
          {destination.photoCount}
        </Badge>
      </Box>

      {/* Content */}
      <Box mt={isCollapsed ? 0 : "md"}>
        <Group
          justify="space-between"
          align="flex-start"
          pr={isCollapsed ? 60 : 0}
        >
          <Text size="lg" fw={700}>
            {destination.name}
          </Text>
          {destination.openNow && !isCollapsed && (
            <Badge variant="light" color="green" size="sm" radius="xl">
              Open Now
            </Badge>
          )}
        </Group>

        <Collapse in={!isCollapsed}>
          <Text size="sm" c="dimmed" mt={4} lineClamp={2}>
            {destination.description}
          </Text>

          {/* Details */}
          <Divider my="sm" />

          <Group justify="space-between" align="center">
            <Group gap="lg">
              <Group gap={6}>
                <IconClock size={18} color="var(--neutral-900)" />
                <Text size="sm" fw={500}>
                  {destination.duration}
                </Text>
              </Group>
              <Group gap={6}>
                <IconTicket size={18} color="var(--neutral-900)" />
                <Text size="sm" fw={500}>
                  {destination.entryFee}
                </Text>
              </Group>
            </Group>

            <Anchor
              href="#"
              size="sm"
              fw={700}
              c="var(--neutral-900)"
              underline="hover"
            >
              View details
            </Anchor>
          </Group>

          {/* Add to Itinerary Button */}
          <Button
            fullWidth
            mt="sm"
            size="sm"
            variant={isInItinerary ? "light" : "filled"}
            color={isInItinerary ? "green" : "var(--neutral-900)"}
            leftSection={
              isInItinerary ? <IconCheck size={16} /> : <IconPlus size={16} />
            }
            onClick={handleAddToItinerary}
            disabled={isInItinerary}
          >
            {isInItinerary ? "Added to Itinerary" : "Add to Itinerary"}
          </Button>
        </Collapse>
      </Box>
    </Paper>
  );
};

export default DestinationCard;
