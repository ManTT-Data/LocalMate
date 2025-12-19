import React from "react";
import PropTypes from "prop-types";
import { Flex, Badge, Text, Group, Switch, Tooltip, Box, ActionIcon } from "@mantine/core";
import { IconMapPin, IconCalendarEvent, IconChevronDown, IconGripVertical } from "@tabler/icons-react";
import { Z_INDEX } from "./constants";
import useItineraryStore from "../../stores/useItineraryStore";

const DayHeader = ({ day, title, date, itineraryName, isCollapsed, onToggle, dragHandleProps }) => {
  const { includeUserLocation, toggleUserLocation } = useItineraryStore();

  return (
    <Box
      mb="md"
      style={{
        background: "linear-gradient(to right, rgba(0, 191, 166, 0.08), transparent)",
        borderRadius: "12px",
        overflow: "hidden",
      }}
    >
      <Flex
        justify="space-between"
        align="center"
        py="sm"
        px="md"
        onClick={onToggle}
        style={{
          cursor: "pointer",
          borderLeft: "3px solid",
          borderImage: "linear-gradient(to bottom, #00bfa6, #0891B2) 1",
          userSelect: "none",
        }}
      >
        <Group gap="sm">
          <Box {...dragHandleProps} style={{ cursor: 'grab', display: 'flex', alignItems: 'center' }}>
            <IconGripVertical size={18} color="var(--mantine-color-gray-4)" />
          </Box>
          <ActionIcon
            variant="subtle"
            color="gray"
            onClick={(e) => {
              e.stopPropagation();
              onToggle();
            }}
            style={{
              transform: isCollapsed ? "rotate(-90deg)" : "rotate(0deg)",
              transition: "transform 0.2s ease",
            }}
          >
            <IconChevronDown size={18} />
          </ActionIcon>
          <Badge
            size="lg"
            radius="md"
            variant="gradient"
            gradient={{ from: 'teal', to: 'cyan', deg: 135 }}
            style={{
              fontWeight: 700,
              padding: "8px 12px",
            }}
          >
            Day {day}
          </Badge>
          {title && (
            <Text fw={600} size="md" c="dark">
              {title}
            </Text>
          )}
        </Group>
        <Group gap="md">
          <Tooltip
            label="Start route from your current location"
            position="left"
            withArrow
          >
            <Switch
              checked={includeUserLocation}
              onChange={toggleUserLocation}
              size="sm"
              color="teal"
              thumbIcon={
                includeUserLocation ? <IconMapPin size={12} stroke={3} /> : null
              }
              label={
                <Text size="xs" fw={500} c="dimmed">
                  My location
                </Text>
              }
              onClick={(e) => e.stopPropagation()}
            />
          </Tooltip>
          {date && (
            <Group gap={4}>
              <IconCalendarEvent size={14} color="var(--mantine-color-gray-5)" />
              <Text size="xs" c="dimmed" fw={500}>
                {date}
              </Text>
            </Group>
          )}
        </Group>
      </Flex>
    </Box>
  );
};

DayHeader.propTypes = {
  day: PropTypes.number.isRequired,
  title: PropTypes.string,
  date: PropTypes.string,
  itineraryName: PropTypes.string,
  isCollapsed: PropTypes.bool,
  onToggle: PropTypes.func,
  dragHandleProps: PropTypes.object,
};

export default React.memo(DayHeader);

