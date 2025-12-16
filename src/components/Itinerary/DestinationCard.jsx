import React from "react";
import PropTypes from "prop-types";
import {
  Box,
  Flex,
  Text,
  Badge,
  Button,
  ActionIcon,
  Tooltip,
} from "@mantine/core";
import { IconCheck, IconX, IconReplace } from "@tabler/icons-react";
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
  onRemove,
  onReplace,
  badge,
}) => {
  return (
    <Flex
      gap="sm"
      align="flex-start"
      pos="relative"
      style={{
        "&:hover .action-buttons": {
          opacity: 1,
        },
      }}
      onMouseEnter={(e) => {
        const buttons = e.currentTarget.querySelector(".action-buttons");
        if (buttons) buttons.style.opacity = "1";
      }}
      onMouseLeave={(e) => {
        const buttons = e.currentTarget.querySelector(".action-buttons");
        if (buttons) buttons.style.opacity = "0";
      }}
    >
      {/* Action Buttons - Top Right */}
      <Box
        pos="absolute"
        top={-8}
        right={-8}
        style={{
          display: "flex",
          gap: 4,
          opacity: 0,
          transition: "opacity 0.2s ease",
          zIndex: 10,
        }}
        className="action-buttons"
      >
        {onReplace && (
          <Tooltip label="Replace destination" position="top" withArrow>
            <ActionIcon
              size="sm"
              variant="subtle"
              color="blue"
              radius="xl"
              onClick={(e) => {
                e.stopPropagation();
                onReplace();
              }}
            >
              <IconReplace size={14} />
            </ActionIcon>
          </Tooltip>
        )}
        {onRemove && (
          <Tooltip label="Remove from itinerary" position="top" withArrow>
            <ActionIcon
              size="sm"
              variant="subtle"
              color="red"
              radius="xl"
              onClick={(e) => {
                e.stopPropagation();
                onRemove();
              }}
            >
              <IconX size={14} />
            </ActionIcon>
          </Tooltip>
        )}
      </Box>

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
          ⭐{" "}
          <Text span c="black">
            {destination.rating}
          </Text>{" "}
          • {destination.type}
        </Text>
        <Text size="xs" c="dimmed">
          {destination.description}
        </Text>

        {/* Booking Status or Action Button */}
        {badge ? (
          <Badge
            size="xs"
            color={badge.color || "green"}
            variant="light"
            mt={4}
            leftSection={badge.icon}
          >
            {badge.text}
          </Badge>
        ) : isBooked ? (
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
  onRemove: PropTypes.func,
  onReplace: PropTypes.func,
  badge: PropTypes.shape({
    text: PropTypes.string.isRequired,
    color: PropTypes.string,
    icon: PropTypes.node,
  }),
};

export default React.memo(DestinationCard);
