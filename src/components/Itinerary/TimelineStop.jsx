import React, { useCallback, useState } from "react";
import PropTypes from "prop-types";
import { Box, Paper } from "@mantine/core";
import useItineraryStore from "../../stores/useItineraryStore";
import BookingModal from "../Booking/BookingModal";
import TimelineDot from "./TimelineDot";
import TravelBadge from "./TravelBadge";
import DestinationCard from "./DestinationCard";
import StartLocationCard from "./StartLocationCard";
import { COLORS, ANIMATIONS } from "./constants";

const TimelineStop = ({ stop, onItemClick, provided, snapshot, dayIndex }) => {
  const isDraggable = !!provided; // Check if component is within a Draggable
  const isDragging = snapshot?.isDragging || false;

  // Zustand store
  const { lastBookedStopId, removeStop, updateStop } = useItineraryStore();

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

  // Memoize remove handler
  const handleRemove = useCallback(() => {
    if (dayIndex !== undefined && stop.id) {
      removeStop(dayIndex, stop.id);
    }
  }, [dayIndex, stop.id, removeStop]);

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

      {/* Content Card */}
      <Paper
        p="sm"
        radius="md"
        withBorder
        shadow={isDragging ? "lg" : "xs"}
        style={{
          cursor: isDraggable && stop.destination ? "grab" : "default",
          transition: `all ${ANIMATIONS.TRANSITION_DURATION}`,
          opacity: isDragging ? 0.9 : 1,
          transform: isDragging ? "rotate(2deg)" : "none",
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
