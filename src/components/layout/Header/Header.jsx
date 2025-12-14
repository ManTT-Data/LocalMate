import React from "react";
import {
  Group,
  Text,
  Anchor,
  ActionIcon,
  Avatar,
  Divider,
} from "@mantine/core";
import { IconBell, IconMapSearch } from "@tabler/icons-react";
import { navigationLinks, userProfile } from "../../../data/mockData";

const Header = ({ onToggleDarkMode, isDarkMode }) => {
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
          {navigationLinks.map((link) => (
            <Anchor
              key={link.id}
              href={link.href}
              fw={link.active ? 600 : 500}
              c={link.active ? "dark" : "dimmed"}
              underline="never"
              size="sm"
              style={{
                transition: "color 0.2s",
              }}
            >
              {link.label}
            </Anchor>
          ))}
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
