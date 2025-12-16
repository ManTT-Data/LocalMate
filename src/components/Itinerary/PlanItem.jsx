import React, { useCallback } from "react";
import PropTypes from "prop-types";
import {
  Box,
  Flex,
  Text,
  Badge,
  Paper,
  Group,
  ActionIcon,
  Tooltip,
} from "@mantine/core";
import { IconMapPin, IconX, IconRefresh } from "@tabler/icons-react";
import TimelineDot from "./TimelineDot";
import DragHandle from "./DragHandle";
import { SIZES, ANIMATIONS } from "./constants";

const PlanItem = ({ item, provided, snapshot, onRemove }) => {
  // Memoize remove handler
  const handleRemove = useCallback(() => {
    onRemove(item.itemId);
  }, [onRemove, item.itemId]);

  return (
    <Box
      ref={provided.innerRef}
      {...provided.draggableProps}
      pos="relative"
      pl={SIZES.CONTENT_PADDING_LEFT}
      pb="lg"
      style={{
        opacity: snapshot.isDragging ? 0.8 : 1,
      }}
    >
      {/* Timeline Dot */}
      <TimelineDot type="plan-item" icon={IconMapPin} />

      {/* Content Card */}
      <Paper
        p="sm"
        radius="md"
        withBorder
        shadow={snapshot.isDragging ? "lg" : "xs"}
        style={{
          cursor: "grab",
          transition: `all ${ANIMATIONS.TRANSITION_DURATION}`,
          borderColor: snapshot.isDragging
            ? "var(--mantine-color-green-5)"
            : undefined,
        }}
      >
        <Flex gap="sm" align="flex-start">
          {/* Drag Handle */}
          <DragHandle
            dragHandleProps={provided.dragHandleProps}
            isDragging={snapshot.isDragging}
          />

          {/* Image */}
          {item.destination?.image && (
            <Box
              w={SIZES.THUMBNAIL_SIZE}
              h={SIZES.THUMBNAIL_SIZE}
              style={{
                borderRadius: "8px",
                backgroundImage: `url("${item.destination.image}")`,
                backgroundSize: "cover",
                backgroundPosition: "center",
                flexShrink: 0,
              }}
            />
          )}

          {/* Info */}
          <Box style={{ flex: 1, minWidth: 0 }}>
            <Text size="sm" fw={700} truncate>
              {item.name}
            </Text>
            <Text size="xs" c="dimmed">
              {item.category}
            </Text>
            <Badge size="xs" color="green" variant="light" mt={4}>
              Added to plan
            </Badge>
          </Box>

          {/* Actions */}
          <Group gap={4}>
            <Tooltip label="Replace">
              <ActionIcon variant="subtle" color="gray" size="sm">
                <IconRefresh size={16} />
              </ActionIcon>
            </Tooltip>
            <Tooltip label="Remove">
              <ActionIcon
                variant="subtle"
                color="red"
                size="sm"
                onClick={handleRemove}
              >
                <IconX size={16} />
              </ActionIcon>
            </Tooltip>
          </Group>
        </Flex>
      </Paper>
    </Box>
  );
};

PlanItem.propTypes = {
  item: PropTypes.shape({
    itemId: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    category: PropTypes.string.isRequired,
    destination: PropTypes.shape({
      image: PropTypes.string,
    }),
  }).isRequired,
  provided: PropTypes.object.isRequired, // From @hello-pangea/dnd
  snapshot: PropTypes.object.isRequired, // From @hello-pangea/dnd
  onRemove: PropTypes.func.isRequired,
};

// Memoize component with custom comparison
export default React.memo(PlanItem, (prevProps, nextProps) => {
  // Re-render if item changes
  if (prevProps.item !== nextProps.item) return false;
  // Re-render if onRemove changes
  if (prevProps.onRemove !== nextProps.onRemove) return false;
  // Re-render if dragging state changes
  if (prevProps.snapshot?.isDragging !== nextProps.snapshot?.isDragging)
    return false;
  // Otherwise, skip re-render
  return true;
});
