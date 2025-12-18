import React from "react";
import PropTypes from "prop-types";
import { Flex, Badge, Text, Group, Switch, Tooltip } from "@mantine/core";
import { IconMapPin } from "@tabler/icons-react";
import { Z_INDEX } from "./constants";
import useItineraryStore from "../../stores/useItineraryStore";

const DayHeader = ({ day, title, date, itineraryName }) => {
  const { includeUserLocation, toggleUserLocation } = useItineraryStore();

  return (
    <Flex
      justify="space-between"
      align="center"
      mb="md"
      bg="white"
      py="xs"
      style={{
        // position: "sticky",
        top: 0,
        zIndex: Z_INDEX.STICKY_HEADER,
        borderBottom: "1px solid var(--neutral-900)",
      }}
    >
      <Group gap="xs">
        <Badge color="black" variant="outline" size="lg" radius="sm">
          Day {day}
        </Badge>
        {itineraryName && (
          <Text fw={700} size="md" c="dimmed">
            {itineraryName} -
          </Text>
        )}
        <Text fw={700} size="md">
          {title}
        </Text>
      </Group>
      <Group gap="sm">
        <Tooltip
          label="Start route from your current location"
          position="left"
          withArrow
        >
          <Switch
            checked={includeUserLocation}
            onChange={toggleUserLocation}
            size="sm"
            color="blue"
            thumbIcon={
              includeUserLocation ? <IconMapPin size={12} stroke={3} /> : null
            }
            label={
              <Text size="xs" fw={500}>
                Start from my location
              </Text>
            }
          />
        </Tooltip>
        <Text size="xs" c="dimmed" fw={500}>
          {date}
        </Text>
      </Group>
    </Flex>
  );
};

DayHeader.propTypes = {
  day: PropTypes.number.isRequired,
  title: PropTypes.string.isRequired,
  date: PropTypes.string.isRequired,
  itineraryName: PropTypes.string,
};

export default React.memo(DayHeader);
