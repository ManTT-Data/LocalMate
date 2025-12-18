import React, { useState, useRef, useEffect } from "react";
import { useLocation } from "react-router-dom";
import {
  Box,
  Group,
  TextInput,
  ActionIcon,
  Button,
  CloseButton,
  Image,
} from "@mantine/core";
import {
  IconMicrophone,
  IconPhoto,
  IconSend,
  IconX,
} from "@tabler/icons-react";
import SuggestionChip from "../SuggestionChip/SuggestionChip";

const MessageComposer = ({
  onSendMessage,
  disabled = false,
  loading = false,
}) => {
  const [message, setMessage] = useState("");
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const imageInputRef = useRef(null);
  const location = useLocation();

  // Define suggestion chips based on current page
  const getSuggestionChips = () => {
    // AiMapView page (home)
    if (location.pathname === "/map") {
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
    // AiMapView page (home)
    else if (location.pathname === "/booking") {
      return [
        { id: 1, icon: "edit", label: "Modify" },
        { id: 2, icon: "payments", label: "Change payment" },
      ];
    }
    // Default fallback
    return [];
  };

  const suggestionChips = getSuggestionChips();

  // Handle paste event for images
  useEffect(() => {
    const handlePaste = (e) => {
      const items = e.clipboardData?.items;
      if (!items) return;

      for (const item of items) {
        if (item.type.startsWith("image/")) {
          e.preventDefault();
          const file = item.getAsFile();
          if (!file) continue;

          if (file.size > 10 * 1024 * 1024) {
            alert("Image too large (max 10MB)");
            return;
          }

          handleImageSelect(file);
          return;
        }
      }
    };

    document.addEventListener("paste", handlePaste);
    return () => document.removeEventListener("paste", handlePaste);
  }, []);

  const handleImageSelect = (file) => {
    if (!file.type.startsWith("image/")) {
      alert("Please select an image file!");
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      alert("Image too large (max 10MB)");
      return;
    }

    setImageFile(file);
    const url = URL.createObjectURL(file);
    setImagePreview(url);
  };

  const handleImageUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      handleImageSelect(file);
    }
  };

  const handleRemoveImage = () => {
    setImageFile(null);
    setImagePreview(null);
    if (imageInputRef.current) {
      imageInputRef.current.value = "";
    }
  };

  const handleSend = () => {
    if (message.trim() || imageFile) {
      onSendMessage(message, imageFile);
      setMessage("");
      handleRemoveImage();
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
      {/* Image Preview */}
      {imagePreview && (
        <Box
          mb="sm"
          style={{
            position: "relative",
            display: "inline-block",
          }}
        >
          <Image
            src={imagePreview}
            alt="Preview"
            radius="md"
            style={{
              maxWidth: 200,
              maxHeight: 150,
              objectFit: "cover",
            }}
          />
          <CloseButton
            icon={<IconX size={16} />}
            onClick={handleRemoveImage}
            style={{
              position: "absolute",
              top: 4,
              right: 4,
              backgroundColor: "rgba(0, 0, 0, 0.6)",
              color: "white",
            }}
            size="sm"
            radius="xl"
          />
        </Box>
      )}

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
          <input
            ref={imageInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageUpload}
            style={{ display: "none" }}
          />
          <ActionIcon
            variant="subtle"
            color={imageFile ? "blue" : "gray"}
            size="lg"
            radius="md"
            title="Upload Image (or paste with Ctrl+V)"
            onClick={() => imageInputRef.current?.click()}
          >
            <IconPhoto size={20} />
          </ActionIcon>

          {/* Send Button */}
          <Button
            onClick={handleSend}
            size="sm"
            radius="md"
            disabled={disabled || (!message.trim() && !imageFile)}
            loading={loading}
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
