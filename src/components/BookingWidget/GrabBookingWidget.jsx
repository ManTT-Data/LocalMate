import React from "react";
import { Paper, Group, Box, Text, Button, Avatar } from "@mantine/core";
import { IconArrowRight } from "@tabler/icons-react";
import { grabBooking } from "../../data/mockData";

const GrabBookingWidget = () => {
  return (
    <Paper
      p="md"
      radius="xl"
      shadow="xl"
      withBorder
      style={{
        pointerEvents: "auto",
        transition: "all 0.3s",
      }}
      styles={{
        root: {
          "&:hover": {
            boxShadow: "var(--mantine-shadow-xl)",
          },
        },
      }}
    >
      {/* Header */}
      <Group justify="space-between" mb="md">
        <Group gap="sm">
          <Avatar
            size="sm"
            radius="xl"
            style={{
              backgroundColor: "#00B14F",
              fontWeight: 700,
              fontSize: "10px",
            }}
            color="white"
          >
            Grab
          </Avatar>
          <Text size="sm" fw={700}>
            Ride Recommendation
          </Text>
        </Group>
        <Text size="xs" c="dimmed">
          {grabBooking.eta}
        </Text>
      </Group>

      {/* Car Selection */}
      <Paper
        p="sm"
        radius="lg"
        withBorder
        mb="md"
        style={{
          cursor: "pointer",
          transition: "all 0.2s",
          backgroundColor: "var(--mantine-color-gray-0)",
        }}
        styles={{
          root: {
            "&:hover": {
              borderColor: "rgba(19, 182, 236, 0.5)",
            },
          },
        }}
      >
        <Group justify="space-between" wrap="nowrap">
          <Box
            w={48}
            h={32}
            style={{
              backgroundImage: `url("${grabBooking.carImage}")`,
              backgroundSize: "contain",
              backgroundPosition: "center",
              backgroundRepeat: "no-repeat",
            }}
          />
          <Box flex={1}>
            <Text size="sm" fw={700}>
              {grabBooking.carType}
            </Text>
            <Text size="xs" c="dimmed">
              {grabBooking.carDescription}
            </Text>
          </Box>
          <Text size="sm" fw={700}>
            {grabBooking.price}
          </Text>
        </Group>
      </Paper>

      {/* Book Button */}
      <Button
        fullWidth
        size="md"
        radius="lg"
        rightSection={<IconArrowRight size={18} />}
        style={{
          backgroundColor: "var(--neutral-900)",
          transition: "all 0.2s",
        }}
      >
        Book Grab Now
      </Button>
    </Paper>
  );
};

export default GrabBookingWidget;
