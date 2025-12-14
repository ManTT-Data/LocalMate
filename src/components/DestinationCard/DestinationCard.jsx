import React from "react";
import { Paper, Box, Group, Text, Badge, Anchor, Divider } from "@mantine/core";
import { IconClock, IconTicket, IconCamera } from "@tabler/icons-react";
import { destinations } from "../../data/mockData";

const DestinationCard = ({ destination = destinations[0] }) => {
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
      {/* Image */}
      <Box
        h={128}
        style={{
          borderRadius: "var(--mantine-radius-lg)",
          backgroundImage: `url("${destination.image}")`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <Badge
          variant="filled"
          color="dark"
          size="sm"
          radius="md"
          leftSection={<IconCamera size={12} />}
          style={{
            position: "absolute",
            top: "0.5rem",
            right: "0.5rem",
            backdropFilter: "blur(8px)",
          }}
        >
          {destination.photoCount}
        </Badge>
      </Box>

      {/* Content */}
      <Box mt="md">
        <Group justify="space-between" align="flex-start">
          <Text size="lg" fw={700}>
            {destination.name}
          </Text>
          {destination.openNow && (
            <Badge variant="light" color="green" size="sm" radius="xl">
              Open Now
            </Badge>
          )}
        </Group>

        <Text size="sm" c="dimmed" mt={4} lineClamp={2}>
          {destination.description}
        </Text>

        {/* Details */}
        <Divider my="sm" />

        <Group justify="space-between" align="center">
          <Group gap="lg">
            <Group gap={6}>
              <IconClock size={18} color="var(--neutral-900)" />
              <Text size="sm" fw={500}>
                {destination.duration}
              </Text>
            </Group>
            <Group gap={6}>
              <IconTicket size={18} color="var(--neutral-900)" />
              <Text size="sm" fw={500}>
                {destination.entryFee}
              </Text>
            </Group>
          </Group>

          <Anchor
            href="#"
            size="sm"
            fw={700}
            c="var(--neutral-900)"
            underline="hover"
          >
            View details
          </Anchor>
        </Group>
      </Box>
    </Paper>
  );
};

export default DestinationCard;
