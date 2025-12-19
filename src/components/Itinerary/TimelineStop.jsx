import React, { useCallback, useState } from "react";
import PropTypes from "prop-types";
import { Box, Paper, Text, ActionIcon, Group } from "@mantine/core";
import { motion, useMotionValue, useTransform } from "framer-motion";
import { IconTrash } from "@tabler/icons-react";
import { modals } from "@mantine/modals";
import { notifications } from "@mantine/notifications";
import useItineraryStore from "../../stores/useItineraryStore";
import BookingModal from "../Booking/BookingModal";
import TimelineDot from "./TimelineDot";
import TravelBadge from "./TravelBadge";
import DestinationCard from "./DestinationCard";
import StartLocationCard from "./StartLocationCard";
import { COLORS, ANIMATIONS } from "./constants";

const TimelineStop = ({ stop, onItemClick, provided, snapshot, dayIndex }) => {
  const x = useMotionValue(0);
  const opacity = useTransform(x, [-100, -50, 0], [1, 0.5, 0]);
  const scale = useTransform(x, [-100, -50, 0], [1, 0.8, 0.5]);

  const isDraggable = !!provided; // Check if component is within a Draggable
  const isDragging = snapshot?.isDragging || false;

  // Zustand store
  const { lastBookedStopId, currentItinerary, deleteStopBackend, updateStop } =
    useItineraryStore();

  // Booking modal state
  const [bookingModal, setBookingModal] = useState({
    opened: false,
    serviceType: null,
  });

  // Check if this stop is highlighted (last booked)
  const isHighlighted = stop.id === lastBookedStopId;
  const isBooked = stop.isBooked;

  // Memoize click handler
  const handleClick = useCallback(() => {
    onItemClick?.(stop);
  }, [onItemClick, stop]);

  // Open booking modal
  const handleBookService = useCallback((serviceType, e) => {
    e?.stopPropagation();
    setBookingModal({ opened: true, serviceType });
  }, []);

  // Close booking modal
  const closeBookingModal = useCallback(() => {
    setBookingModal({ opened: false, serviceType: null });
  }, []);

  // Memoize book ticket handler
  const handleBookTicket = useCallback(
    (e) => {
      handleBookService("ticket", e);
    },
    [handleBookService]
  );

  // Memoize view details handler
  const handleViewDetails = useCallback(() => {
    // Empty function for now
  }, []);

  // Memoize remove handler with backend persistence
  const handleRemove = useCallback(() => {
    console.log("🗑️ Remove clicked", {
      dayIndex,
      stopId: stop.id,
      currentItinerary,
    });

    modals.openConfirmModal({
      title: "Remove Stop",
      children:
        "Are you sure you want to remove this stop from your itinerary?",
      labels: { confirm: "Remove", cancel: "Cancel" },
      confirmProps: { color: "red" },
      onConfirm: async () => {
        console.log("✅ User confirmed delete");

        if (dayIndex !== undefined && stop.id && currentItinerary?.id) {
          console.log("🔄 Deleting stop from backend...", {
            itineraryId: currentItinerary.id,
            dayIndex,
            stopId: stop.id,
          });

          try {
            await deleteStopBackend(currentItinerary.id, dayIndex, stop.id);
            notifications.show({
              title: "Success",
              message: "Stop removed from itinerary",
              color: "green",
            });
          } catch (error) {
            console.error("❌ Error removing stop:", error);
            notifications.show({
              title: "Error",
              message: "Failed to remove stop",
              color: "red",
            });
          }
        } else {
          console.error("❌ Missing required data:", {
            dayIndex,
            stopId: stop.id,
            currentItinerary,
          });
          notifications.show({
            title: "Error",
            message: "Cannot delete - missing itinerary information",
            color: "red",
          });
        }
      },
    });
  }, [dayIndex, stop.id, currentItinerary, deleteStopBackend]);

  // Memoize replace handler
  const handleReplace = useCallback(() => {
    // TODO: Open a modal or sidebar to select a new destination
    console.log("Replace destination:", stop.id);
    // For now, just log - you can implement a destination picker modal later
  }, [stop.id]);

  const content = (
    <Box pos="relative" pl={32} pb={32} className="group">
      {/* Timeline Dot */}
      <TimelineDot
        type={stop.type === "destination" ? "destination" : "start"}
        isTopPick={stop.isTopPick}
      />

      {/* Content Card with Swipe Action */}
      <Box pos="relative" style={{ overflow: "hidden", borderRadius: "8px" }}>
        {/* Underlay Action (Delete) */}
        <Box
          pos="absolute"
          right={0}
          top={0}
          bottom={0}
          w={100}
          bg="red.6"
          style={{
            zIndex: 1,
            borderRadius: "8px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <motion.div style={{ opacity, scale }}>
            <Group gap={4} c="white" style={{ cursor: "pointer" }} onClick={(e) => { e.stopPropagation(); handleRemove(); }}>
              <IconTrash size={20} />
              <Text fw={700} size="xs">DELETE</Text>
            </Group>
          </motion.div>
        </Box>

        <motion.div
          style={{ x, zIndex: 2, position: "relative" }}
          drag="x"
          dragConstraints={{ left: -100, right: 0 }}
          dragElastic={0.1}
          onDragEnd={(_, info) => {
            if (info.offset.x < -80) {
              // Option 1: Just snap to revealed state or 
              // Option 2: Automatically trigger delete modal
              // For now, let's just keep it revealed
            } else {
              x.set(0);
            }
          }}
        >
          <Paper
            p="sm"
            radius="md"
            withBorder
            shadow={isDragging ? "lg" : "xs"}
            style={{
              cursor: isDraggable && stop.destination ? "grab" : "default",
              transition: isDragging ? "none" : `all ${ANIMATIONS.TRANSITION_DURATION}`,
              opacity: isDragging ? 0.9 : 1,
              transform: isDragging ? "rotate(2deg)" : "none",
              backgroundColor: "white",
              border: isHighlighted
                ? `2px solid ${COLORS.HIGHLIGHT_BORDER}`
                : isBooked
                  ? `1px solid ${COLORS.BOOKED_BORDER}`
                  : undefined,
              animation: isHighlighted
                ? `pulse ${ANIMATIONS.PULSE_DURATION} ease-in-out infinite`
                : undefined,
            }}
            onClick={handleClick}
            className={
              isDraggable && stop.destination ? "hover:border-blue-500" : ""
            }
          >
            <Box pos="relative">
              {stop.destination ? (
                <DestinationCard
                  destination={stop.destination}
                  isDraggable={isDraggable}
                  isDragging={isDragging}
                  dragHandleProps={provided?.dragHandleProps}
                  isBooked={isBooked}
                  bookingDetails={stop.bookingDetails}
                  onBookTicket={handleBookTicket}
                  onViewDetails={handleViewDetails}
                  onRemove={handleRemove}
                  onReplace={handleReplace}
                />
              ) : (
                <StartLocationCard
                  name={stop.name}
                  locationName={stop.locationName}
                />
              )}
            </Box>
          </Paper>
        </motion.div>
      </Box>

      {/* Travel Info Badge */}
      <TravelBadge travel={stop.nextTravel} onBook={handleBookService} />
    </Box>
  );

  // If draggable, wrap with provided props
  if (isDraggable) {
    return (
      <>
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          style={{
            ...provided.draggableProps.style,
          }}
        >
          {content}
        </div>

        {/* Booking Modal */}
        <BookingModal
          opened={bookingModal.opened}
          onClose={closeBookingModal}
          stop={stop}
          dayIndex={dayIndex}
          serviceType={bookingModal.serviceType}
        />
      </>
    );
  }

  // Otherwise, return plain content with modal
  return (
    <>
      {content}

      {/* Booking Modal */}
      <BookingModal
        opened={bookingModal.opened}
        onClose={closeBookingModal}
        stop={stop}
        dayIndex={dayIndex}
        serviceType={bookingModal.serviceType}
      />
    </>
  );
};

TimelineStop.propTypes = {
  stop: PropTypes.shape({
    type: PropTypes.string,
    name: PropTypes.string,
    locationName: PropTypes.string,
    isTopPick: PropTypes.bool,
    destination: PropTypes.shape({
      name: PropTypes.string,
      type: PropTypes.string,
      image: PropTypes.string,
    }),
    nextTravel: PropTypes.shape({
      duration: PropTypes.string,
      label: PropTypes.string,
    }),
  }).isRequired,
  onItemClick: PropTypes.func,
  provided: PropTypes.object, // From @hello-pangea/dnd Draggable
  snapshot: PropTypes.object, // From @hello-pangea/dnd Draggable
  dayIndex: PropTypes.number, // Index of the day
};

// Memoize component with custom comparison to prevent unnecessary re-renders
export default React.memo(TimelineStop, (prevProps, nextProps) => {
  // Re-render if stop data changes
  if (prevProps.stop !== nextProps.stop) return false;
  // Re-render if onItemClick changes
  if (prevProps.onItemClick !== nextProps.onItemClick) return false;
  // Re-render if dragging state changes
  if (prevProps.snapshot?.isDragging !== nextProps.snapshot?.isDragging)
    return false;
  // Re-render if dayIndex changes
  if (prevProps.dayIndex !== nextProps.dayIndex) return false;
  // Otherwise, skip re-render
  return true;
});
