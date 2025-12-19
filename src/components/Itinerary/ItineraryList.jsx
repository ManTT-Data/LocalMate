import React, { useCallback, useMemo } from "react";
import PropTypes from "prop-types";
import { Box, Text, Button, Collapse } from "@mantine/core";
import { IconPlus } from "@tabler/icons-react";
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";
import useItineraryStore from "../../stores/useItineraryStore";
import useGeolocation from "../../hooks/useGeolocation";
import DayHeader from "./DayHeader";
import TimelineStop from "./TimelineStop";
import { DND_TYPES, COLORS, SIZES, Z_INDEX } from "./constants";

const ItineraryList = ({ onItemClick }) => {
  // Collapsed days state
  const [collapsedDays, setCollapsedDays] = React.useState({});

  const toggleDayCollapse = useCallback((dayIndex) => {
    setCollapsedDays((prev) => ({
      ...prev,
      [dayIndex]: !prev[dayIndex],
    }));
  }, []);

  // Use unified Zustand store
  const {
    itineraryItems,
    reorderStops,
    reorderDays,
    currentItinerary,
    includeUserLocation,
  } = useItineraryStore();

  // Get user location
  const { location: userLocation } = useGeolocation();

  // Memoized drag end handler for better performance
  const handleDragEnd = useCallback(
    (result) => {
      // Early return if no valid destination
      if (!result.destination) return;

      const { source, destination, type } = result;

      // Skip if dropped in same position
      if (
        source.droppableId === destination.droppableId &&
        source.index === destination.index
      ) {
        return;
      }

      // Handle plan items drag
      if (type === DND_TYPES.PLAN_ITEMS) {
        const items = Array.from(plan.items);
        const [reorderedItem] = items.splice(source.index, 1);
        items.splice(destination.index, 0, reorderedItem);
        reorderPlanItems(items);
        return;
      }

      // Handle days reordering
      if (type === DND_TYPES.DAYS) {
        const items = Array.from(itineraryItems);
        const [reorderedDay] = items.splice(source.index, 1);
        items.splice(destination.index, 0, reorderedDay);

        // Correct day numbers
        const correctedItems = items.map((item, idx) => ({
          ...item,
          day: idx + 1,
        }));

        reorderDays(correctedItems);
        return;
      }

      // Handle stops drag (static itinerary stops)
      if (type === DND_TYPES.STOPS) {
        const dayId = result.source.droppableId; // stops-0, stops-1, etc.
        const dayIndex = parseInt(dayId.split("-")[1]);
        const dayStops = [...itineraryItems[dayIndex].stops];
        const [reorderedStop] = dayStops.splice(source.index, 1);
        dayStops.splice(destination.index, 0, reorderedStop);

        // Update Zustand store (will trigger route recalculation)
        reorderStops(dayIndex, dayStops);
      }
    },
    [itineraryItems, reorderStops, reorderDays]
  );

  return (
    <Box
      component="div"
      flex={1}
      style={{ overflowY: "auto" }}
      p="md"
      className="custom-scrollbar"
    >
      <DragDropContext onDragEnd={handleDragEnd}>
        <Droppable droppableId="all-days" type={DND_TYPES.DAYS}>
          {(provided) => (
            <Box {...provided.droppableProps} ref={provided.innerRef}>
              {itineraryItems.map((dayItem, dayIndex) => (
                <Draggable
                  key={`day-drag-${dayIndex}`}
                  draggableId={`day-drag-${dayIndex}`}
                  index={dayIndex}
                >
                  {(provided) => (
                    <Box
                      ref={provided.innerRef}
                      {...provided.draggableProps}
                      mb="xl"
                    >
                      {/* Day Header */}
                      <DayHeader
                        day={dayItem.day}
                        // title={dayItem.title}
                        date={dayItem.date}
                        // itineraryName={currentItinerary?.title}
                        isCollapsed={!!collapsedDays[dayIndex]}
                        onToggle={() => toggleDayCollapse(dayIndex)}
                        dragHandleProps={provided.dragHandleProps}
                      />

                      {/* Timeline */}
                      <Box pos="relative" ml="xs">
                        {/* Timeline Vertical Line */}
                        <Box
                          pos="absolute"
                          left={SIZES.TIMELINE_LINE_LEFT_OFFSET}
                          top={8}
                          bottom={0}
                          w={SIZES.TIMELINE_LINE_WIDTH}
                          bg={COLORS.TIMELINE_LINE}
                          style={{
                            zIndex: Z_INDEX.TIMELINE_LINE,
                            display: collapsedDays[dayIndex] ? "none" : "block",
                          }}
                        />

                        <Collapse in={!collapsedDays[dayIndex]}>

                          {/* Draggable stops from itineraryData */}
                          {dayItem.stops && (
                            <Droppable
                              droppableId={`stops-${dayIndex}`}
                              type={DND_TYPES.STOPS}
                            >
                              {(provided, snapshot) => {
                                // Prepare stops array with optional user location
                                let stopsToRender = dayItem.stops;

                                // If includeUserLocation is enabled and we have user location
                                if (
                                  includeUserLocation &&
                                  userLocation.loaded &&
                                  userLocation.coordinates.lat
                                ) {
                                  // Create user location stop
                                  const userLocationStop = {
                                    id: "user-location-start",
                                    type: "start",
                                    name: "Your Location",
                                    locationName: "Current Position",
                                    location: {
                                      lat: userLocation.coordinates.lat,
                                      lng: userLocation.coordinates.lng,
                                    },
                                    snapshot: {
                                      lat: userLocation.coordinates.lat,
                                      lng: userLocation.coordinates.lng,
                                    },
                                    isUserLocation: true,
                                  };

                                  // Prepend to stops
                                  stopsToRender = [userLocationStop, ...dayItem.stops];
                                }

                                return (
                                  <Box
                                    {...provided.droppableProps}
                                    ref={provided.innerRef}
                                    style={{
                                      backgroundColor: snapshot.isDraggingOver
                                        ? "rgba(59, 130, 246, 0.05)"
                                        : "transparent",
                                      borderRadius: "8px",
                                      transition: "background-color 0.2s",
                                    }}
                                  >
                                    {stopsToRender.map((stop, stopIndex) => (
                                      <Draggable
                                        key={
                                          stop.isUserLocation
                                            ? "user-location-start"
                                            : `stop-${dayIndex}-${stopIndex}`
                                        }
                                        draggableId={
                                          stop.isUserLocation
                                            ? "user-location-start"
                                            : `stop-${dayIndex}-${stopIndex}`
                                        }
                                        index={stopIndex}
                                        isDragDisabled={
                                          stop.isUserLocation || !stop.destination
                                        } // Disable drag for user location and non-destinations
                                      >
                                        {(provided, snapshot) => (
                                          <TimelineStop
                                            stop={stop}
                                            onItemClick={onItemClick}
                                            provided={provided}
                                            snapshot={snapshot}
                                            dayIndex={dayIndex}
                                          />
                                        )}
                                      </Draggable>
                                    ))}
                                    {provided.placeholder}
                                  </Box>
                                );
                              }}
                            </Droppable>
                          )}

                          <Box pl={SIZES.CONTENT_PADDING_LEFT} pt="xs">
                            <Button
                              variant="default"
                              fullWidth
                              style={{ borderStyle: "dashed" }}
                              leftSection={<IconPlus size={18} />}
                              c="dimmed"
                            >
                              Add another stop
                            </Button>
                          </Box>
                        </Collapse>
                      </Box>
                    </Box>
                  )}
                </Draggable>
              ))}
              {provided.placeholder}
            </Box>
          )}
        </Droppable>
      </DragDropContext>
    </Box>
  );
};

ItineraryList.propTypes = {
  onItemClick: PropTypes.func,
};

export default React.memo(ItineraryList);
