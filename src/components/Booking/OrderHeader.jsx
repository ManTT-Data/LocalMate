import React from "react";
import { Group, Text, Badge, Box } from "@mantine/core";

/**
 * Order header component
 * Displays order ID, title, and status
 */
const OrderHeader = ({ orderId, title, description, status = "pending" }) => {
  const getStatusColor = () => {
    switch (status) {
      case "confirmed":
        return "green";
      case "pending":
        return "yellow";
      case "cancelled":
        return "red";
      default:
        return "gray";
    }
  };

  const getStatusLabel = () => {
    switch (status) {
      case "confirmed":
        return "Confirmed";
      case "pending":
        return "Pending Confirmation";
      case "cancelled":
        return "Cancelled";
      default:
        return "Unknown";
    }
  };

  return (
    <Box mb="xl">
      <Group justify="space-between" align="flex-start" mb="xs">
        <Text size="xl" fw={700}>
          {title}
        </Text>
        <Text size="sm" c="dimmed" fw={500}>
          Order ID: #{orderId}
        </Text>
      </Group>
      <Text size="sm" c="dimmed" maw={600} mb="md">
        {description}
      </Text>
    </Box>
  );
};

export default OrderHeader;
