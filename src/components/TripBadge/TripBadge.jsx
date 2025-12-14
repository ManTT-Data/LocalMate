import React from "react";
import { Paper, Group, Stack, Text, ThemeIcon } from "@mantine/core";
import { tripContext } from "../../data/mockData";

const TripBadge = () => {
  return (
    <Paper
      px="md"
      py="sm"
      radius="lg"
      shadow="sm"
      withBorder
      style={{
        backgroundColor: "rgba(255, 255, 255, 0.9)",
        backdropFilter: "blur(12px)",
        pointerEvents: "auto",
      }}
    >
      <Group gap="md">
        <Stack gap={0} align="flex-end">
          <Text size="10px" tt="uppercase" fw={700} c="dimmed" lts={1.5}>
            Trip Context
          </Text>
          <Text size="sm" fw={700}>
            {tripContext.type} • {tripContext.budget}
          </Text>
        </Stack>
        <ThemeIcon size="lg" radius="xl" variant="light" color="black">
          <span
            className="material-symbols-outlined"
            style={{ fontSize: "18px" }}
          >
            {tripContext.icon}
          </span>
        </ThemeIcon>
      </Group>
    </Paper>
  );
};

export default TripBadge;
