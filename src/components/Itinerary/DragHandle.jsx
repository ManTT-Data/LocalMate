import React from "react";
import PropTypes from "prop-types";
import { Box, ThemeIcon } from "@mantine/core";
import { IconGripVertical } from "@tabler/icons-react";
import { SIZES } from "./constants";

/**
 * Reusable drag handle component for draggable items
 */
const DragHandle = ({ dragHandleProps, isDragging = false }) => {
  return (
    <Box
      {...dragHandleProps}
      style={{
        cursor: "grab",
        paddingTop: 4,
        display: "flex",
        opacity: isDragging ? 0.5 : 1,
      }}
    >
      <ThemeIcon variant="transparent" color="gray" size="sm">
        <IconGripVertical size={SIZES.DRAG_HANDLE_SIZE} />
      </ThemeIcon>
    </Box>
  );
};

DragHandle.propTypes = {
  dragHandleProps: PropTypes.object,
  isDragging: PropTypes.bool,
};

export default React.memo(DragHandle);
