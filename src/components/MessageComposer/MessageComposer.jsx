import React, { useState } from "react";
import { useLocation } from "react-router-dom";
import { Box, Group, TextInput, ActionIcon, Button } from "@mantine/core";
import { IconMicrophone, IconPhoto, IconSend } from "@tabler/icons-react";
import SuggestionChip from "../SuggestionChip/SuggestionChip";

const MessageComposer = ({ onSendMessage }) => {
  const [message, setMessage] = useState("");
  const location = useLocation();

  // Define suggestion chips based on current page
  const getSuggestionChips = () => {
    // AiMapView page (home)
    if (location.pathname === "/") {
      return [
        { id: 1, icon: "restaurant", label: "Seafood nearby" },
        { id: 2, icon: "local_cafe", label: "Coffee shops" },
        { id: 3, icon: "local_taxi", label: "Book ride" },
      ];
    }
    // AiItinerary page
    else if (location.pathname === "/ai-itinerary") {
      return [
        { id: 1, icon: "add_location", label: "Add stop" },
        { id: 2, icon: "schedule", label: "Change time" },
      ];
    }
    // Default fallback
    return [];
  };

  const suggestionChips = getSuggestionChips();

  const handleSend = () => {
    if (message.trim()) {
      onSendMessage(message);
      setMessage("");
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Box
      p="md"
      style={{
        borderTop: "1px solid var(--mantine-color-gray-3)",
        backgroundColor: "white",
      }}
    >
      {/* Suggestion Chips */}
      <Group gap="xs" mb="md" style={{ overflowX: "auto", flexWrap: "nowrap" }}>
        {suggestionChips.map((chip) => (
          <SuggestionChip
            key={chip.id}
            icon={chip.icon}
            label={chip.label}
            onClick={() => setMessage(chip.label)}
          />
        ))}
      </Group>

      {/* Input Field */}
      <Box
        style={{
          display: "flex",
          alignItems: "center",
          gap: "0.5rem",
          backgroundColor: "var(--mantine-color-gray-1)",
          borderRadius: "var(--mantine-radius-lg)",
          padding: "0.25rem",
          border: "1px solid transparent",
          transition: "all 0.2s",
        }}
      >
        <TextInput
          flex={1}
          placeholder="Ask about places, upload a photo, or plan a route..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          variant="unstyled"
          size="sm"
          styles={{
            input: {
              padding: "0.5rem 0.75rem",
            },
          }}
        />

        <Group gap={4} pr={4}>
          {/* Upload Image */}
          <ActionIcon
            variant="subtle"
            color="gray"
            size="lg"
            radius="md"
            title="Upload Image"
          >
            <IconPhoto size={20} />
          </ActionIcon>

          {/* Send Button */}
          <Button
            onClick={handleSend}
            size="sm"
            radius="md"
            style={{
              backgroundColor: "var(--neutral-900)",
              transition: "all 0.2s",
            }}
          >
            <IconSend size={20} />
          </Button>
        </Group>
      </Box>
    </Box>
  );
};

export default MessageComposer;
