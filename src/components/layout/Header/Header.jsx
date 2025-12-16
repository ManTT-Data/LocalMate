import React from "react";
import {
  Group,
  Text,
  Anchor,
  ActionIcon,
  Avatar,
  Divider,
} from "@mantine/core";
import { Link, useLocation } from "react-router-dom";
import { IconBell, IconMapSearch } from "@tabler/icons-react";
import { userProfile } from "../../../data/mockData";

// Navigation links (moved from mockData.js)
const navigationLinks = [
  { id: 1, label: "Home", href: "/", active: false },
  { id: 2, label: "My Trips", href: "/ai-itinerary", active: false },
  { id: 3, label: "My Bookings", href: "/booking", active: false },
  { id: 4, label: "Saved Places", href: "/saved", active: false },
];

const Header = ({ onToggleDarkMode, isDarkMode }) => {
  const location = useLocation();

  return (
    <Group
      h={60}
      px="xl"
      justify="space-between"
      style={{
        borderBottom: "1px solid var(--mantine-color-gray-3)",
        backgroundColor: "white",
      }}
    >
      {/* Logo and Brand */}
      <Group gap="md">
        <IconMapSearch size={32} stroke={1.5} />
        <Text size="lg" fw={700}>
          LocalMate Agent
        </Text>
      </Group>

      {/* Navigation and Actions */}
      <Group gap="xl">
        {/* Navigation Links */}
        <Group gap="xl" visibleFrom="md">
          {navigationLinks.map((link) => {
            const isActive = location.pathname === link.href;

            return (
              <Anchor
                key={link.id}
                component={Link}
                to={link.href}
                fw={isActive ? 600 : 500}
                c={isActive ? "dark" : "dimmed"}
                underline="never"
                size="sm"
                style={{
                  transition: "color 0.2s",
                }}
              >
                {link.label}
              </Anchor>
            );
          })}
        </Group>

        {/* Divider */}
        <Divider orientation="vertical" visibleFrom="md" />

        {/* Action Buttons */}
        <Group gap="xs">
          {/* Notifications */}
          <ActionIcon
            variant="light"
            color="gray"
            size="lg"
            radius="xl"
            aria-label="Notifications"
          >
            <IconBell size={20} stroke={1.5} />
          </ActionIcon>

          {/* User Profile */}
          <Avatar
            src={userProfile.avatar}
            alt={userProfile.name}
            radius="xl"
            size="md"
            style={{ cursor: "pointer" }}
          />
        </Group>
      </Group>
    </Group>
  );
};

export default Header;
