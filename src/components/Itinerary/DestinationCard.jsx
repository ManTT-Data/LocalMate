import React from "react";
import PropTypes from "prop-types";
import { Box, Flex, Text, Badge, Button } from "@mantine/core";
import { IconCheck } from "@tabler/icons-react";
import { SIZES } from "./constants";
import DragHandle from "./DragHandle";

/**
 * Card component for displaying destination information
 */
const DestinationCard = ({
  destination,
  isDraggable = false,
  isDragging = false,
  dragHandleProps,
  isBooked = false,
  bookingDetails,
  onBookTicket,
  onViewDetails,
}) => {
  return (
    <Flex gap="sm" align="flex-start">
      {/* Drag Handle */}
      {isDraggable && (
        <DragHandle dragHandleProps={dragHandleProps} isDragging={isDragging} />
      )}

      {/* Thumbnail Image */}
      <Box
        w={SIZES.THUMBNAIL_SIZE}
        h={SIZES.THUMBNAIL_SIZE}
        style={{
          borderRadius: "8px",
          backgroundImage: `url("${destination.image}")`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          flexShrink: 0,
        }}
      />

      {/* Info */}
      <Box style={{ flex: 1, minWidth: 0 }}>
        <Text size="sm" fw={700} truncate>
          {destination.name}
        </Text>
        <Text size="xs" c="dimmed">
          {destination.type}
        </Text>

        {/* Booking Status or Action Button */}
        {isBooked ? (
          <Badge
            size="xs"
            color="green"
            variant="light"
            mt={4}
            leftSection={<IconCheck size={12} />}
          >
            Booked
          </Badge>
        ) : bookingDetails?.bookable ? (
          <Button
            variant="subtle"
            size="compact-xs"
            p={0}
            mt={4}
            color="blue"
            onClick={onBookTicket}
          >
            Book Ticket
          </Button>
        ) : (
          <Button
            variant="subtle"
            size="compact-xs"
            p={0}
            mt={4}
            color="blue"
            onClick={onViewDetails}
          >
            View Details
          </Button>
        )}
      </Box>
    </Flex>
  );
};

DestinationCard.propTypes = {
  destination: PropTypes.shape({
    name: PropTypes.string.isRequired,
    type: PropTypes.string.isRequired,
    image: PropTypes.string,
  }).isRequired,
  isDraggable: PropTypes.bool,
  isDragging: PropTypes.bool,
  dragHandleProps: PropTypes.object,
  isBooked: PropTypes.bool,
  bookingDetails: PropTypes.shape({
    bookable: PropTypes.bool,
  }),
  onBookTicket: PropTypes.func,
  onViewDetails: PropTypes.func,
};

export default React.memo(DestinationCard);
