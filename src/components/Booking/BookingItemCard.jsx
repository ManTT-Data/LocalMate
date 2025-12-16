import React from "react";
import {
  Paper,
  Group,
  Stack,
  Text,
  Badge,
  ActionIcon,
  Box,
} from "@mantine/core";
import { IconEdit, IconTrash, IconUsers, IconClock } from "@tabler/icons-react";

/**
 * Reusable booking item card component
 * Displays individual booking details with actions
 */
const BookingItemCard = ({ booking, onEdit, onRemove }) => {
  const getIconColor = () => {
    switch (booking.bookingType) {
      case "transportation":
        return "#00B14F";
      case "ticket":
        return "#3b82f6";
      case "reservation":
        return "#f97316";
      default:
        return "gray";
    }
  };

  const renderActionButtons = () => {
    if (booking.bookingType === "transportation") {
      return (
        <Group gap="md">
          <ActionIcon
            variant="subtle"
            color="gray"
            size="sm"
            onClick={() => onEdit?.(booking)}
          >
            <IconEdit size={18} />
          </ActionIcon>
          <Text
            size="sm"
            fw={700}
            c="dimmed"
            style={{ cursor: "pointer" }}
            onClick={() => onEdit?.(booking)}
          >
            Edit
          </Text>
          <ActionIcon
            variant="subtle"
            color="red"
            size="sm"
            onClick={() => onRemove?.(booking)}
          >
            <IconTrash size={18} />
          </ActionIcon>
          <Text
            size="sm"
            fw={700}
            c="red"
            style={{ cursor: "pointer" }}
            onClick={() => onRemove?.(booking)}
          >
            Remove
          </Text>
        </Group>
      );
    }

    if (booking.bookingType === "ticket") {
      return (
        <Group gap="md">
          <ActionIcon variant="subtle" color="gray" size="sm">
            <IconUsers size={18} />
          </ActionIcon>
          <Text
            size="sm"
            fw={700}
            c="dimmed"
            style={{ cursor: "pointer" }}
            onClick={() => onEdit?.(booking)}
          >
            Modify Guests
          </Text>
          <ActionIcon
            variant="subtle"
            color="red"
            size="sm"
            onClick={() => onRemove?.(booking)}
          >
            <IconTrash size={18} />
          </ActionIcon>
          <Text
            size="sm"
            fw={700}
            c="red"
            style={{ cursor: "pointer" }}
            onClick={() => onRemove?.(booking)}
          >
            Remove
          </Text>
        </Group>
      );
    }

    if (booking.bookingType === "reservation") {
      return (
        <Group gap="md">
          <ActionIcon variant="subtle" color="gray" size="sm">
            <IconClock size={18} />
          </ActionIcon>
          <Text
            size="sm"
            fw={700}
            c="dimmed"
            style={{ cursor: "pointer" }}
            onClick={() => onEdit?.(booking)}
          >
            Change Time
          </Text>
          <ActionIcon
            variant="subtle"
            color="red"
            size="sm"
            onClick={() => onRemove?.(booking)}
          >
            <IconTrash size={18} />
          </ActionIcon>
          <Text
            size="sm"
            fw={700}
            c="red"
            style={{ cursor: "pointer" }}
            onClick={() => onRemove?.(booking)}
          >
            Cancel
          </Text>
        </Group>
      );
    }

    return null;
  };

  return (
    <Paper
      p="lg"
      radius="xl"
      withBorder
      style={{
        transition: "all 0.2s ease",
        cursor: "pointer",
      }}
      styles={{
        root: {
          "&:hover": {
            boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
          },
        },
      }}
    >
      <Stack gap="md">
        {/* Header */}
        <Group
          justify="space-between"
          pb="sm"
          style={{ borderBottom: "1px solid var(--mantine-color-gray-2)" }}
        >
          <Group gap="sm">
            <Box
              style={{
                backgroundColor: `${getIconColor()}15`,
                color: getIconColor(),
                padding: "8px",
                borderRadius: "12px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <span
                className="material-symbols-outlined"
                style={{ fontSize: 24 }}
              >
                {booking.icon}
              </span>
            </Box>
            <div>
              <Text fw={700} size="md">
                {booking.category}
              </Text>
              <Text size="xs" c="dimmed">
                {booking.categoryBadge}
              </Text>
            </div>
          </Group>
          <Badge size="md" variant="light" color="gray">
            <Group gap={4}>
              <span
                className="material-symbols-outlined"
                style={{ fontSize: 14 }}
              >
                schedule
              </span>
              {booking.scheduledTime}
            </Group>
          </Badge>
        </Group>

        {/* Content */}
        <Group align="flex-start" gap="md">
          {/* Image or Icon */}
          {booking.image ? (
            <Box
              w={96}
              h={96}
              style={{
                borderRadius: "12px",
                backgroundImage: `url("${booking.image}")`,
                backgroundSize: "cover",
                backgroundPosition: "center",
                border: "1px solid var(--mantine-color-gray-2)",
                flexShrink: 0,
              }}
            />
          ) : (
            <Box
              w={96}
              h={96}
              style={{
                borderRadius: "12px",
                backgroundColor: "var(--mantine-color-gray-1)",
                border: "1px solid var(--mantine-color-gray-2)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              <span
                className="material-symbols-outlined"
                style={{ fontSize: 48, color: getIconColor() }}
              >
                directions_car
              </span>
            </Box>
          )}

          {/* Details */}
          <Stack gap="xs" style={{ flex: 1 }}>
            <Group justify="space-between">
              <div>
                <Text fw={700} size="lg">
                  {booking.serviceName}
                </Text>
                {booking.bookingType === "transportation" && (
                  <Group gap="xs" mt={8}>
                    <Badge size="sm" variant="light">
                      {booking.bookingDetails.from}
                    </Badge>
                    <span
                      className="material-symbols-outlined"
                      style={{
                        fontSize: 14,
                        color: "var(--mantine-color-gray-5)",
                      }}
                    >
                      arrow_right_alt
                    </span>
                    <Badge size="sm" variant="light">
                      {booking.bookingDetails.to}
                    </Badge>
                  </Group>
                )}
                {booking.bookingType === "ticket" && (
                  <Group gap="md" mt={8}>
                    <Badge size="sm" variant="light">
                      {booking.bookingDetails.guests}
                    </Badge>
                    <Text size="sm" c="dimmed">
                      •
                    </Text>
                    <Text size="sm" c="dimmed">
                      {booking.bookingDetails.ticketType}
                    </Text>
                  </Group>
                )}
                {booking.bookingType === "reservation" && (
                  <Group gap="md" mt={8}>
                    <Badge size="sm" variant="light">
                      {booking.bookingDetails.tableType}
                    </Badge>
                    <Text size="sm" c="dimmed">
                      •
                    </Text>
                    <Text size="sm" c="dimmed">
                      {booking.bookingDetails.mealType}
                    </Text>
                  </Group>
                )}
              </div>
              <div style={{ textAlign: "right" }}>
                <Text fw={700} size="lg">
                  {booking.priceDisplay}
                </Text>
                {booking.bookingType === "ticket" && (
                  <Text size="xs" c="dimmed">
                    {booking.bookingDetails.pricePerTicket} x{" "}
                    {booking.bookingDetails.quantity}
                  </Text>
                )}
                {booking.bookingType === "reservation" && (
                  <Text size="xs" c="dimmed">
                    {booking.bookingDetails.paymentNote}
                  </Text>
                )}
              </div>
            </Group>

            {/* Actions */}
            <Box
              mt="sm"
              pt="sm"
              style={{ borderTop: "1px solid var(--mantine-color-gray-1)" }}
            >
              {renderActionButtons()}
            </Box>
          </Stack>
        </Group>
      </Stack>
    </Paper>
  );
};

export default BookingItemCard;
