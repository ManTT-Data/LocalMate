import React from "react";
import { Paper, Group, Box, Image, Text } from "@mantine/core";
import { IconStar } from "@tabler/icons-react";

const InfoCard = ({ data }) => {
  return (
    <Paper
      p="sm"
      radius="lg"
      withBorder
      style={{
        transition: "all 0.2s",
        cursor: "pointer",
      }}
      styles={{
        root: {
          "&:hover": {
            borderColor: "rgba(19, 182, 236, 0.3)",
          },
        },
      }}
    >
      <Group gap="md" wrap="nowrap">
        {/* Image */}
        <Box
          w={64}
          h={64}
          style={{
            borderRadius: "var(--mantine-radius-md)",
            backgroundImage: `url("${data.image}")`,
            backgroundSize: "cover",
            backgroundPosition: "center",
            flexShrink: 0,
          }}
        />

        {/* Info */}
        <Box>
          <Text fw={700} size="sm">
            {data.name}
          </Text>

          {/* Rating */}
          <Group gap={4} mt={2}>
            <IconStar size={14} fill="#f59e0b" color="#f59e0b" />
            <Text size="xs" fw={500}>
              {data.rating}
            </Text>
            <Text size="xs" c="dimmed">
              ({data.reviews})
            </Text>
          </Group>

          {/* Open Status */}
          <Text size="xs" c="dimmed" mt={4}>
            Open until {data.openUntil}
          </Text>
        </Box>
      </Group>
    </Paper>
  );
};

export default InfoCard;
