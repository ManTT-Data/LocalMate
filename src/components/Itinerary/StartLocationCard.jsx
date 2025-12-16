import React from "react";
import PropTypes from "prop-types";
import { Box, Flex, Text, ThemeIcon } from "@mantine/core";
import { IconHome } from "@tabler/icons-react";

/**
 * Card component for displaying start location
 */
const StartLocationCard = ({ name, locationName }) => {
  return (
    <Flex gap="sm" align="center">
      <ThemeIcon size={40} radius="md" color="gray" variant="light">
        <IconHome size={20} />
      </ThemeIcon>
      <Box>
        <Text size="sm" fw={700}>
          {name}
        </Text>
        <Text size="xs" c="dimmed">
          {locationName}
        </Text>
      </Box>
    </Flex>
  );
};

StartLocationCard.propTypes = {
  name: PropTypes.string.isRequired,
  locationName: PropTypes.string.isRequired,
};

export default React.memo(StartLocationCard);
