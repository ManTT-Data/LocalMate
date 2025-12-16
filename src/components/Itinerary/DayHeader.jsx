import React from "react";
import PropTypes from "prop-types";
import { Flex, Badge, Text, Group } from "@mantine/core";
import { Z_INDEX } from "./constants";

const DayHeader = ({ day, title, date }) => {
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
        <Text fw={700} size="md">
          {title}
        </Text>
      </Group>
      <Text size="xs" c="dimmed" fw={500}>
        {date}
      </Text>
    </Flex>
  );
};

DayHeader.propTypes = {
  day: PropTypes.number.isRequired,
  title: PropTypes.string.isRequired,
  date: PropTypes.string.isRequired,
};

export default React.memo(DayHeader);
