import React from "react";
import PropTypes from "prop-types";
import { Box, ThemeIcon } from "@mantine/core";
import { IconMapPin } from "@tabler/icons-react";
import { COLORS, SIZES, Z_INDEX } from "./constants";

/**
 * Timeline dot component with different variants
 */
const TimelineDot = ({ type, isTopPick = false, icon: CustomIcon }) => {
  const getColor = () => {
    if (isTopPick) return COLORS.TOP_PICK;
    if (type === "destination") return COLORS.DESTINATION;
    if (type === "plan-item") return COLORS.PLAN_ITEM;
    return COLORS.START_LOCATION;
  };

  const getVariant = () => {
    return type === "destination" && !isTopPick ? "filled" : "light";
  };

  const Icon = CustomIcon || IconMapPin;

  return (
    <Box
      pos="absolute"
      left={SIZES.TIMELINE_DOT_LEFT_OFFSET}
      top={SIZES.TIMELINE_DOT_TOP_OFFSET}
      style={{ zIndex: Z_INDEX.TIMELINE_DOT }}
    >
      <ThemeIcon
        size={SIZES.TIMELINE_DOT}
        radius="xl"
        color={getColor()}
        variant={getVariant()}
        style={{
          border: `${SIZES.TIMELINE_DOT_BORDER}px solid white`,
          boxShadow: "0 1px 2px rgba(0,0,0,0.1)",
        }}
      >
        {type === "destination" && !isTopPick ? (
          <Box w={8} h={8} bg="white" style={{ borderRadius: "50%" }} />
        ) : (
          <Icon size={14} />
        )}
      </ThemeIcon>
    </Box>
  );
};

TimelineDot.propTypes = {
  type: PropTypes.oneOf(["start", "destination", "plan-item"]).isRequired,
  isTopPick: PropTypes.bool,
  icon: PropTypes.elementType,
};

export default React.memo(TimelineDot);
