import React, { useState, useEffect } from "react";
import AppLayout from "../components/layout/AppLayout/AppLayout";
import ItineraryList from "../components/Itinerary/ItineraryList";
import ItineraryMap from "../components/Itinerary/ItineraryMap";
import ItinerarySkeleton from "../components/Itinerary/ItinerarySkeleton";
import ContextualToolbar from "../components/ContextualToolbar/ContextualToolbar";
import EditItineraryModal from "../components/Itinerary/EditItineraryModal";
import { modals } from "@mantine/modals";
import { notifications } from "@mantine/notifications";
import {
  fetchUserItinerariesAPI,
  fetchItineraryByIdAPI,
  deleteItineraryAPI,
} from "../apis/itineraryService";
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
  Drawer,
} from "@mantine/core";
import { useMediaQuery, useDisclosure } from "@mantine/hooks";
import {
  IconShare,
  IconAdjustments,
  IconFileTypePdf,
  IconWand,
  IconMapPin,
  IconAlertCircle,
  IconTrash,
} from "@tabler/icons-react";

const AiItinerary = () => {
  const [activeTab, setActiveTab] = useState("itinerary"); // map, itinerary, bookings
  const [itineraryMetadata, setItineraryMetadata] = useState(null);
  const [currentItineraryId, setCurrentItineraryId] = useState(null); // Store itinerary ID for direct stop operations
  const [editModalOpened, setEditModalOpened] = useState(false);
  const isMobile = useMediaQuery("(max-width: 768px)");
  const [drawerOpened, { toggle: toggleDrawer, close: closeDrawer }] = useDisclosure(false);


  // Zustand store - unified state management
  const {
    itineraryItems,
    isLoading,
    error,
    setItinerary,
    setCurrentItinerary,
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
        // Fetch all itineraries for the user
        const itineraries = await fetchUserItinerariesAPI();

        if (itineraries && itineraries.length > 0) {
          // Store the itinerary ID for direct stop operations
          const itineraryId = itineraries[0].id;
          setCurrentItineraryId(itineraryId);

          // Get the first (most recent) itinerary with full details
          const firstItinerary = await fetchItineraryByIdAPI(itineraryId);

          // Set metadata from backend
          if (firstItinerary) {
            setItineraryMetadata({
              id: itineraryId, // Include ID in metadata
              title: firstItinerary.title,
              startDate: firstItinerary.start_date,
              endDate: firstItinerary.end_date,
              totalDays: firstItinerary.total_days,
              dateRange: formatDateRange(
                firstItinerary.start_date,
                firstItinerary.end_date
              ),
              duration: `${firstItinerary.total_days} ${firstItinerary.total_days === 1 ? "day" : "days"
                }`,
            });

            // Set itinerary items (transformed days array)
            setItinerary(firstItinerary.days || []);

            // IMPORTANT: Set currentItinerary in store for delete functionality
            setCurrentItinerary(firstItinerary);
          }
        } else {
          // No itineraries found
          setCurrentItineraryId(null);
          setItinerary([]);
          setItineraryMetadata({
            title: "No Itinerary",
            dateRange: "",
            duration: "0 days",
          });
        }
      } catch (err) {
        setError(err.message);
      }
    };

    loadItinerary();
  }, [setItinerary, setLoading, setError]);

  // Helper function to format date range
  const formatDateRange = (startDate, endDate) => {
    if (!startDate || !endDate) return "";

    const start = new Date(startDate);
    const end = new Date(endDate);

    const months = [
      "Jan",
      "Feb",
      "Mar",
      "Apr",
      "May",
      "Jun",
      "Jul",
      "Aug",
      "Sep",
      "Oct",
      "Nov",
      "Dec",
    ];

    return `${months[start.getMonth()]} ${start.getDate()} - ${months[end.getMonth()]
      } ${end.getDate()}`;
  };

  /**
   * Helper function to add a stop directly to itinerary_stops table
   * This can be called from child components (ItineraryList, MapPanel, etc.)
   *
   * @example
   * // Add a destination to Day 1
   * await handleAddStop(0, {
   *   place_id: "marble-mountains",
   *   arrival_time: "09:00",
   *   stay_minutes: 90,
   *   notes: "Visit early morning",
   *   tags: ["sightseeing", "cultural"],
   *   snapshot: { name: "Marble Mountains", category: "Attraction" }
   * });
   */
  const handleAddStop = async (dayIndex, stopData) => {
    if (!currentItineraryId) {
      console.error("No itinerary ID available");
      return;
    }

    try {
      const { addStopAPI } = await import("../apis/stopService");

      // Prepare stop data with day_index (backend uses 1-indexed)
      const backendStopData = {
        ...stopData,
        day_index: dayIndex + 1, // Convert 0-based to 1-based
      };

      // Add stop directly to itinerary_stops table
      const response = await addStopAPI(currentItineraryId, backendStopData);

      console.log("✅ Stop added successfully:", response);

      // Refresh itinerary to show the new stop
      const updatedItinerary = await fetchItineraryByIdAPI(currentItineraryId);

      if (updatedItinerary?.days) {
        setItinerary(updatedItinerary.days);
      }

      return response;
    } catch (error) {
      console.error("❌ Error adding stop:", error);
      setError(error.message);
      throw error;
    }
  };

  // Handle edit itinerary
  const handleEditItinerary = () => {
    setEditModalOpened(true);
  };

  // Handle delete itinerary
  const handleDeleteItinerary = () => {
    modals.openConfirmModal({
      title: "Delete Itinerary",
      children: (
        <Text size="sm">
          Are you sure you want to delete this itinerary? This action cannot be
          undone.
        </Text>
      ),
      labels: { confirm: "Delete", cancel: "Cancel" },
      confirmProps: { color: "red" },
      onConfirm: async () => {
        try {
          await deleteItineraryAPI(currentItineraryId);
          notifications.show({
            title: "Success",
            message: "Itinerary deleted successfully",
            color: "green",
          });
          // Reload page or redirect to itinerary list
          window.location.reload();
        } catch (error) {
          console.error("Error deleting itinerary:", error);
          notifications.show({
            title: "Error",
            message: "Failed to delete itinerary",
            color: "red",
          });
        }
      },
    });
  };

  const currentItinerary = itineraryItems[0]; // Displaying Day 1 for now

  // Show loading state
  if (isLoading) {
    return (
      <AppLayout>
        <Flex
          flex={1}
          bg="gray.0"
          style={{ position: "relative", overflow: "hidden", height: "100%" }}
        >
          {/* Content Area Skeleton */}
          <Flex flex={1} pt={76} h="100%" style={{ overflow: "hidden" }} w="100%">
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
              <ItinerarySkeleton />
            </Paper>
            <Box flex={1} h="100%" bg="gray.1">
              <Skeleton h="100%" w="100%" />
            </Box>
          </Flex>
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
        <Flex
          flex={1}
          pt={76}
          h="100%"
          style={{ overflow: "hidden" }}
          w="100%"
          direction={isMobile ? "column" : "row"}
        >
          {/* Left Panel: Itinerary List or Drawer for Mobile */}
          {!isMobile ? (
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
                      {itineraryMetadata?.title || "Loading..."}
                    </Text>
                    <Text size="xs" c="dimmed">
                      {itineraryMetadata?.dateRange || ""}{" "}
                      {itineraryMetadata?.dateRange && "•"}{" "}
                      {itineraryMetadata?.duration || ""}
                    </Text>
                  </Box>
                  <Group gap="xs">
                    <ActionIcon
                      variant="subtle"
                      color="gray"
                      size="lg"
                      onClick={handleEditItinerary}
                    >
                      <IconAdjustments size={20} />
                    </ActionIcon>
                    <ActionIcon
                      variant="subtle"
                      color="gray"
                      size="lg"
                      onClick={handleDeleteItinerary}
                    >
                      <IconTrash size={20} />
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
          ) : (
            <Drawer
              opened={drawerOpened}
              onClose={closeDrawer}
              position="bottom"
              size="80%"
              title={itineraryMetadata?.title || "Itinerary"}
              styles={{
                content: { borderRadius: "24px 24px 0 0" },
                header: { padding: "16px 20px" },
                body: { padding: 0, overflow: "hidden", height: "100%" },
              }}
              zIndex={2000}
            >
              <Flex direction="column" h="100%">
                <Box px="md" pb="md">
                  <Text size="xs" c="dimmed">
                    {itineraryMetadata?.dateRange || ""} • {itineraryMetadata?.duration || ""}
                  </Text>
                </Box>
                <Box flex={1} style={{ overflow: "hidden" }}>
                  <ItineraryList
                    onItemClick={(item) => {
                      console.log("Clicked", item);
                      closeDrawer();
                    }}
                  />
                </Box>
                <Box p="md" bg="gray.0" style={{ borderTop: "1px solid var(--mantine-color-gray-3)" }}>
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
                    Optimize
                  </Button>
                </Box>
              </Flex>
            </Drawer>
          )}

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

            {/* Mobile Toggle Button */}
            {isMobile && (
              <Button
                pos="absolute"
                bottom={24}
                left="50%"
                style={{ transform: "translateX(-50%)", zIndex: 1000 }}
                radius="xl"
                size="md"
                className="bg-slate-900 border-none shadow-2xl"
                leftSection={<IconMapPin size={18} />}
                onClick={toggleDrawer}
              >
                View Itinerary
              </Button>
            )}
          </Box>
        </Flex>
      </Flex>

      {/* Edit Itinerary Modal */}
      <EditItineraryModal
        opened={editModalOpened}
        onClose={() => setEditModalOpened(false)}
        itinerary={itineraryMetadata}
      />
    </AppLayout>
  );
};

export default AiItinerary;
