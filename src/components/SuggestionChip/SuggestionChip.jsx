import React from "react";
import { Button } from "@mantine/core";

const SuggestionChip = ({ icon, label, onClick }) => {
  return (
    <Button
      onClick={onClick}
      variant="light"
      color="gray"
      size="xs"
      radius="xl"
      leftSection={
        <span
          className="material-symbols-outlined"
          style={{ fontSize: "16px", color: "var(--neutral-900)" }}
        >
          {icon}
        </span>
      }
      styles={{
        root: {
          flexShrink: 0,
          transition: "all 0.2s",
        },
        section: {
          marginRight: "0.25rem",
        },
      }}
    >
      {label}
    </Button>
  );
};

export default SuggestionChip;
