import React from "react";
import {
  Group,
  Text,
  Anchor,
  ActionIcon,
  Avatar,
  Divider,
  Badge,
} from "@mantine/core";
import { Link, useLocation } from "react-router-dom";
import { IconBell, IconMapSearch } from "@tabler/icons-react";
import useUserStore from "../../../stores/useUserStore";
import useAuthStore from "../../../stores/useAuthStore";

const navigationLinks = [
  { id: 1, label: "Home", href: "/", active: false },
  { id: 2, label: "My Trips", href: "/ai-itinerary", active: false },
  { id: 3, label: "My Bookings", href: "/booking", active: false },
  { id: 4, label: "Saved Places", href: "/saved", active: false },
];

const Header = () => {
  const location = useLocation();
  const user = useUserStore((state) => state.user);
  const { getUserName, getUserAvatar, getUserEmail, isAuthenticated } =
    useAuthStore();

  // Use real user from auth store, fallback to test user
  const currentUser = {
    name: getUserName(),
    avatar: getUserAvatar(),
    email: getUserEmail(),
    isTestUser: !isAuthenticated,
  };

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
          <Group gap="xs">
            <Avatar
              src={currentUser?.avatar}
              alt={currentUser?.name || "User"}
              radius="xl"
              size="md"
              style={{ cursor: "pointer" }}
            >
              {!currentUser?.avatar && currentUser?.name
                ? currentUser.name.charAt(0).toUpperCase()
                : null}
            </Avatar>

            {/* Show test user badge in development */}
            {currentUser?.isTestUser && (
              <Badge size="xs" color="yellow" variant="light">
                Test User
              </Badge>
            )}
          </Group>
        </Group>
      </Group>
    </Group>
  );
};

export default Header;
