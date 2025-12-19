import React, { useState } from "react";
import {
  Paper,
  Group,
  Box,
  Text,
  Button,
  Avatar,
  ActionIcon,
  Collapse,
  Modal,
  Image,
  Stack,
} from "@mantine/core";
import {
  IconArrowRight,
  IconChevronDown,
  IconChevronUp,
  IconX,
} from "@tabler/icons-react";
import { grabBooking } from "../../data/mockData";
import grabQR from "../../assets/grabQR.png";

const GrabBookingWidget = ({ onClose }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [qrModalOpened, setQrModalOpened] = useState(false);

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
      <Group justify="space-between" mb={isCollapsed ? 0 : "md"}>
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

        <Group gap={4}>
          {!isCollapsed && (
            <Text size="xs" c="dimmed" mr="xs">
              {grabBooking.eta}
            </Text>
          )}
          <ActionIcon
            size="sm"
            variant="subtle"
            color="gray"
            onClick={(e) => {
              e.stopPropagation();
              setIsCollapsed(!isCollapsed);
            }}
          >
            {isCollapsed ? (
              <IconChevronDown size={16} />
            ) : (
              <IconChevronUp size={16} />
            )}
          </ActionIcon>
          <ActionIcon
            size="sm"
            variant="subtle"
            color="gray"
            onClick={(e) => {
              e.stopPropagation();
              onClose && onClose();
            }}
          >
            <IconX size={16} />
          </ActionIcon>
        </Group>
      </Group>

      <Collapse in={!isCollapsed}>
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
          onClick={() => {
            setQrModalOpened(true);
          }}
        >
          Book Grab Now
        </Button>
      </Collapse>

      {/* QR Code Modal */}
      <Modal
        opened={qrModalOpened}
        onClose={() => setQrModalOpened(false)}
        title="Quét mã QR để đặt Grab"
        centered
        size="md"
        radius="lg"
        zIndex={10000}
      >
        <Stack align="center" gap="md" p="md">
          <Text size="sm" c="dimmed" ta="center">
            Mở ứng dụng Grab và quét mã QR này để đặt xe
          </Text>
          <Image
            src={grabQR}
            alt="Grab QR Code"
            fit="contain"
            style={{
              maxWidth: "100%",
              height: "auto",
            }}
          />
          <Text size="xs" c="dimmed" ta="center">
            {grabBooking.carType} - {grabBooking.price}
          </Text>
          <Button
            fullWidth
            onClick={() => setQrModalOpened(false)}
            variant="default"
          >
            Đóng
          </Button>
        </Stack>
      </Modal>
    </Paper>
  );
};

export default GrabBookingWidget;
