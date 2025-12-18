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
  Badge,
  Stack,
} from "@mantine/core";
import {
  IconArrowRight,
  IconChevronDown,
  IconChevronUp,
  IconX,
  IconStar,
} from "@tabler/icons-react";
import { hotelBooking } from "../../data/mockData";

const HotelBookingWidget = ({ onClose }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);

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
              backgroundColor: "#003580",
              fontWeight: 700,
              fontSize: "10px",
            }}
            color="white"
          >
            B.com
          </Avatar>
          <Text size="sm" fw={700}>
            Hotel Recommendation
          </Text>
        </Group>

        <Group gap={4}>
          {!isCollapsed && (
            <Badge size="xs" color="blue" variant="light" mr="xs">
              {hotelBooking.nights}
            </Badge>
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
        {/* Hotel Selection */}
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
                borderColor: "rgba(0, 53, 128, 0.5)",
              },
            },
          }}
        >
          <Group gap="sm" align="flex-start" wrap="nowrap">
            <Box
              w={80}
              h={60}
              style={{
                backgroundImage: `url("${hotelBooking.hotelImage}")`,
                backgroundSize: "cover",
                backgroundPosition: "center",
                backgroundRepeat: "no-repeat",
                borderRadius: "8px",
                flexShrink: 0,
              }}
            />
            <Stack gap={4} flex={1}>
              <Group gap={4}>
                <IconStar size={14} fill="#fbbf24" color="#fbbf24" />
                <Text size="xs" c="dimmed">
                  {hotelBooking.rating} ({hotelBooking.reviews} reviews)
                </Text>
              </Group>
              <Text size="sm" fw={700} lineClamp={1}>
                {hotelBooking.hotelName}
              </Text>
              <Text size="xs" c="dimmed">
                {hotelBooking.hotelDescription}
              </Text>
              <Text size="xs" c="dimmed">
                {hotelBooking.roomType}
              </Text>
            </Stack>
            <Stack gap={0} align="flex-end">
              <Text size="sm" fw={700}>
                {hotelBooking.price}
              </Text>
              <Text size="xs" c="dimmed">
                {hotelBooking.pricePerNight}
              </Text>
            </Stack>
          </Group>

          {/* Amenities */}
          <Group gap={4} mt="xs">
            {hotelBooking.amenities.map((amenity, index) => (
              <Badge
                key={index}
                size="xs"
                variant="light"
                color="blue"
                radius="sm"
              >
                {amenity}
              </Badge>
            ))}
          </Group>
        </Paper>

        {/* Book Button */}
        <Button
          fullWidth
          size="md"
          radius="lg"
          rightSection={<IconArrowRight size={18} />}
          style={{
            backgroundColor: "#003580",
            transition: "all 0.2s",
          }}
          onClick={() => {
            window.open(hotelBooking.bookingUrl, "_blank");
          }}
        >
          Book on Booking.com
        </Button>
      </Collapse>
    </Paper>
  );
};

export default HotelBookingWidget;
