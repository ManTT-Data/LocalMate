import React, { useState, useEffect } from "react";
import AppLayout from "../components/layout/AppLayout/AppLayout";
import ItineraryList from "../components/Itinerary/ItineraryList";
import ItineraryMap from "../components/Itinerary/ItineraryMap";
import ContextualToolbar from "../components/ContextualToolbar/ContextualToolbar";
import { tripMetadata } from "../data/mockData";
import { fetchItineraryFromBackend } from "../apis/itineraryService";
import useItineraryStore from "../stores/useItineraryStore";
import {
  Box,
  Flex,
  Button,
  Text,
  Paper,
  Group,
  ThemeIcon,
  Badge,
  ActionIcon,
  Tooltip,
  Loader,
  Alert,
} from "@mantine/core";
import {
  IconShare,
  IconAdjustments,
  IconFileTypePdf,
  IconWand,
  IconMapPin,
  IconAlertCircle,
} from "@tabler/icons-react";

const AiItinerary = () => {
  const [activeTab, setActiveTab] = useState("itinerary"); // map, itinerary, bookings

  // Zustand store - unified state management
  const {
    itineraryItems,
    isLoading,
    error,
    setItinerary,
    setLoading,
    setError,
    plan,
    optimizeRoute,
  } = useItineraryStore();

  // Fetch itinerary data on mount
  useEffect(() => {
    const loadItinerary = async () => {
      setLoading(true);
      try {
        const data = await fetchItineraryFromBackend();
        setItinerary(data);
      } catch (err) {
        setError(err.message);
      }
    };

    loadItinerary();
  }, [setItinerary, setLoading, setError]);

  const currentItinerary = itineraryItems[0]; // Displaying Day 1 for now

  // Show loading state
  if (isLoading) {
    return (
      <AppLayout>
        <Flex
          justify="center"
          align="center"
          h="100%"
          direction="column"
          gap="md"
        >
          <Loader size="xl" />
          <Text c="dimmed">Loading your itinerary...</Text>
        </Flex>
      </AppLayout>
    );
  }

  // Show error state
  if (error) {
    return (
      <AppLayout>
        <Flex justify="center" align="center" h="100%" p="md">
          <Alert
            icon={<IconAlertCircle size={16} />}
            title="Error Loading Itinerary"
            color="red"
            variant="light"
            maw={400}
          >
            {error}
          </Alert>
        </Flex>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <Flex
        flex={1}
        bg="gray.0"
        style={{ position: "relative", overflow: "hidden", height: "100%" }}
      >
        {/* Top Floating Bar */}
        <Box
          pos="absolute"
          top={0}
          left={0}
          right={0}
          p="md"
          style={{ zIndex: 20, pointerEvents: "none" }}
        >
          <Flex justify="space-between" align="flex-start">
            <ContextualToolbar />
          </Flex>
        </Box>

        {/* Content Area */}
        <Flex flex={1} pt={76} h="100%" style={{ overflow: "hidden" }} w="100%">
          {/* Left Panel: Itinerary List */}
          <Paper
            width={450}
            miw={450}
            component={Flex}
            direction="column"
            shadow="md"
            radius={0}
            style={{
              zIndex: 10,
              borderRight: "1px solid var(--mantine-color-gray-3)",
            }}
          >
            <Box
              px="md"
              py="md"
              style={{ borderBottom: "1px solid var(--mantine-color-gray-2)" }}
            >
              <Flex justify="space-between" align="center">
                <Box>
                  <Text size="xl" fw={700}>
                    {tripMetadata.title}
                  </Text>
                  <Text size="xs" c="dimmed">
                    {tripMetadata.dateRange} • {tripMetadata.duration}
                  </Text>
                </Box>
                <Group gap="xs">
                  <ActionIcon variant="subtle" color="gray" size="lg">
                    <IconAdjustments size={20} />
                  </ActionIcon>
                  <ActionIcon variant="subtle" color="gray" size="lg">
                    <IconFileTypePdf size={20} />
                  </ActionIcon>
                </Group>
              </Flex>
            </Box>

            <ItineraryList
              onItemClick={(item) => console.log("Clicked", item)}
            />

            <Box
              p="md"
              bg="gray.0"
              style={{ borderTop: "1px solid var(--mantine-color-gray-3)" }}
            >
              <Group justify="space-between" mb="sm">
                <Text size="xs" c="dimmed">
                  Total Places:{" "}
                  <Text span fw={700} c="dark">
                    {plan.items.length}
                  </Text>
                </Text>
                {plan.isOptimized && (
                  <>
                    <Text size="xs" c="dimmed">
                      Distance:{" "}
                      <Text span fw={700} c="dark">
                        {plan.totalDistanceKm} km
                      </Text>
                    </Text>
                    <Text size="xs" c="dimmed">
                      Duration:{" "}
                      <Text span fw={700} c="dark">
                        {plan.estimatedDurationMin} min
                      </Text>
                    </Text>
                  </>
                )}
              </Group>
              <Button
                fullWidth
                size="md"
                radius="xl"
                color={plan.isOptimized ? "green" : "dark"}
                leftSection={<IconWand size={18} />}
                onClick={optimizeRoute}
                disabled={plan.items.length === 0}
                loading={plan.isOptimizing}
              >
                {plan.isOptimizing
                  ? "Optimizing..."
                  : plan.isOptimized
                  ? "Route Optimized ✓"
                  : "Optimize Route & Times"}
              </Button>
            </Box>
          </Paper>

          {/* Right Panel: Map */}
          <Box flex={1} h="100%" pos="relative" bg="gray.1">
            {/* ItineraryMap accepts optional props to customize:
                - center: [lat, lng] - Map center coordinates (default: Da Nang center)
                - zoom: number - Initial zoom level (default: 13)
                - routeColor: string - Route line color (default: "#3b82f6")
                - routeWeight: number - Route line thickness (default: 5)
                - routeOpacity: number - Route line opacity (default: 0.8)
                
                Example:
                <ItineraryMap 
                  stops={currentItinerary.stops}
                  center={[16.0544, 108.2022]}
                  zoom={14}
                  routeColor="#10b981"
                  routeWeight={6}
                />
            */}
            <ItineraryMap dayIndex={0} />
          </Box>
        </Flex>
      </Flex>
    </AppLayout>
  );
};

export default AiItinerary;
