import React, { useCallback, useMemo } from "react";
import PropTypes from "prop-types";
import { Box, Text, Button } from "@mantine/core";
import { IconPlus } from "@tabler/icons-react";
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";
import useItineraryStore from "../../stores/useItineraryStore";
import DayHeader from "./DayHeader";
import TimelineStop from "./TimelineStop";
import PlanItem from "./PlanItem";
import { DND_TYPES, COLORS, SIZES, Z_INDEX } from "./constants";

const ItineraryList = ({ onItemClick }) => {
  // Use unified Zustand store
  const { itineraryItems, reorderStops, plan, removeItem, reorderPlanItems } =
    useItineraryStore();

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

      // Handle stops drag (static itinerary stops)
      if (type === DND_TYPES.STOPS) {
        const dayIndex = parseInt(result.draggableId.split("-")[1]);
        const dayStops = [...itineraryItems[dayIndex].stops];
        const [reorderedStop] = dayStops.splice(source.index, 1);
        dayStops.splice(destination.index, 0, reorderedStop);

        // Update Zustand store (will trigger route recalculation)
        reorderStops(dayIndex, dayStops);
      }
    },
    [plan.items, itineraryItems, reorderPlanItems, reorderStops]
  );

  // Memoized computation to check if there are any plan items
  const hasPlanItems = useMemo(
    () => plan.items.length > 0,
    [plan.items.length]
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
        {itineraryItems.map((dayItem, dayIndex) => (
          <Box key={`day-${dayIndex}`} mb="xl">
            {/* Day Header */}
            <DayHeader
              day={dayItem.day}
              title={dayItem.title}
              date={dayItem.date}
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
                style={{ zIndex: Z_INDEX.TIMELINE_LINE }}
              />

              {/* Draggable stops from itineraryData */}
              {dayItem.stops && (
                <Droppable
                  droppableId={`stops-${dayIndex}`}
                  type={DND_TYPES.STOPS}
                >
                  {(provided, snapshot) => (
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
                      {dayItem.stops.map((stop, stopIndex) => (
                        <Draggable
                          key={`stop-${dayIndex}-${stopIndex}`}
                          draggableId={`stop-${dayIndex}-${stopIndex}`}
                          index={stopIndex}
                          isDragDisabled={!stop.destination} // Only allow dragging destination stops
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
                  )}
                </Droppable>
              )}

              {/* Dynamic plan items with DnD */}
              {hasPlanItems && (
                <Box mb="md">
                  <Text
                    size="sm"
                    fw={700}
                    c="blue"
                    mb="xs"
                    pl={SIZES.CONTENT_PADDING_LEFT}
                  >
                    Your Added Places
                  </Text>
                  <Droppable
                    droppableId="plan-items"
                    type={DND_TYPES.PLAN_ITEMS}
                  >
                    {(provided) => (
                      <Box {...provided.droppableProps} ref={provided.innerRef}>
                        {plan.items.map((item, index) => (
                          <Draggable
                            key={item.itemId}
                            draggableId={item.itemId}
                            index={index}
                          >
                            {(provided, snapshot) => (
                              <PlanItem
                                item={item}
                                provided={provided}
                                snapshot={snapshot}
                                onRemove={removeItem}
                              />
                            )}
                          </Draggable>
                        ))}
                        {provided.placeholder}
                      </Box>
                    )}
                  </Droppable>
                </Box>
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
            </Box>
          </Box>
        ))}
      </DragDropContext>
    </Box>
  );
};

ItineraryList.propTypes = {
  onItemClick: PropTypes.func,
};

export default React.memo(ItineraryList);
