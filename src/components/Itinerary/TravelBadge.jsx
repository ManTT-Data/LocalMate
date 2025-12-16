import React, { useCallback } from "react";
import PropTypes from "prop-types";
import { Box, Badge } from "@mantine/core";
import { IconCar } from "@tabler/icons-react";
import { Z_INDEX } from "./constants";

/**
 * Travel info badge component for displaying travel duration and mode
 */
const TravelBadge = ({ travel, onBook }) => {
  if (!travel) return null;

  const handleClick = useCallback(
    (e) => {
      if (travel.bookable && onBook) {
        e.stopPropagation();
        onBook("grab");
      }
    },
    [travel.bookable, onBook]
  );

  return (
    <Box
      pos="absolute"
      left={16}
      bottom={8}
      style={{ zIndex: Z_INDEX.TRAVEL_BADGE, transform: "translateY(50%)" }}
    >
      <Badge
        variant="outline"
        color="gray"
        size="sm"
        bg="white"
        leftSection={<IconCar size={12} />}
        style={{
          textTransform: "none",
          fontWeight: 500,
          cursor: travel.bookable ? "pointer" : "default",
        }}
        onClick={handleClick}
      >
        {travel.duration}
        {travel.label ? ` • ${travel.label}` : ""}
      </Badge>
    </Box>
  );
};

TravelBadge.propTypes = {
  travel: PropTypes.shape({
    duration: PropTypes.string.isRequired,
    label: PropTypes.string,
    bookable: PropTypes.bool,
  }),
  onBook: PropTypes.func,
};

export default React.memo(TravelBadge);
