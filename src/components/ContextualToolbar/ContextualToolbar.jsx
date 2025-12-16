import React from "react";
import { Paper, Group, Button } from "@mantine/core";
import { Link, useLocation } from "react-router-dom";
import { IconMap, IconCalendar, IconReceipt } from "@tabler/icons-react";

// Contextual tabs data (moved from mockData.js)
const contextualTabs = [
  { id: 1, label: "Map View", icon: IconMap, href: "/" },
  { id: 2, label: "Itinerary", icon: IconCalendar, href: "/ai-itinerary" },
  { id: 3, label: "Bookings", icon: IconReceipt, href: "#" },
];

const ContextualToolbar = () => {
  const location = useLocation();

  return (
    <Paper
      ml={32}
      p={4}
      radius="xl"
      shadow="xs"
      withBorder
      bg="rgba(255, 255, 255, 0.9)"
      style={{ pointerEvents: "auto", backdropFilter: "blur(10px)" }}
    >
      <Group gap="xs">
        {contextualTabs.map((tab) => {
          const isActive = location.pathname === tab.href;
          const IconComponent = tab.icon;

          return (
            <Button
              key={tab.id}
              component={Link}
              to={tab.href}
              variant={isActive ? "light" : "subtle"}
              color={isActive ? "black" : "gray"}
              size="xs"
              radius="lg"
              leftSection={<IconComponent size={18} />}
            >
              {tab.label}
            </Button>
          );
        })}
      </Group>
    </Paper>
  );
};

export default ContextualToolbar;
