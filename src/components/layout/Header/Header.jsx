import React, { useState } from "react";
import {
  Group,
  Text,
  Anchor,
  ActionIcon,
  Avatar,
  Divider,
  Menu,
} from "@mantine/core";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  IconBell,
  IconMapSearch,
  IconSettings,
  IconHistory,
  IconLogout,
} from "@tabler/icons-react";
import useAuthStore from "../../../stores/useAuthStore";
import HistoryModal from "../../../pages/HistoryModal";

const navigationLinks = [
  { id: 1, label: "My Map", href: "/map", active: false },
  { id: 2, label: "My Trips", href: "/ai-itinerary", active: false },
  { id: 3, label: "My Bookings", href: "/booking", active: false },
];

const Header = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { getUserName, getUserAvatar, getUserEmail, isAuthenticated, logout } =
    useAuthStore();

  // State for History Modal
  const [historyModalOpened, setHistoryModalOpened] = useState(false);

  // Get current user from auth store
  const currentUser = isAuthenticated
    ? {
        name: getUserName(),
        avatar: getUserAvatar(),
        email: getUserEmail(),
      }
    : null;

  // Handle logout
  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <>
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

            {/* User Profile with Dropdown Menu */}
            <Menu shadow="md" width={200} position="bottom-end">
              <Menu.Target>
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
              </Menu.Target>

              <Menu.Dropdown>
                <Menu.Label>{currentUser?.name || "User"}</Menu.Label>

                <Menu.Divider />

                {/* <Menu.Item
                  leftSection={<IconSettings size={16} />}
                  onClick={() => navigate("/settings")}
                >
                  Settings
                </Menu.Item> */}

                <Menu.Item
                  leftSection={<IconHistory size={16} />}
                  onClick={() => setHistoryModalOpened(true)}
                >
                  History
                </Menu.Item>

                <Menu.Divider />

                <Menu.Item
                  leftSection={<IconLogout size={16} />}
                  color="red"
                  onClick={handleLogout}
                >
                  Logout
                </Menu.Item>
              </Menu.Dropdown>
            </Menu>
          </Group>
        </Group>
      </Group>

      {/* History Modal */}
      <HistoryModal
        opened={historyModalOpened}
        onClose={() => setHistoryModalOpened(false)}
      />
    </>
  );
};

export default Header;
