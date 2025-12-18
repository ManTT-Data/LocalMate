import React, { useState } from "react";
import { Group, Box, Avatar, Text, Paper, Image, Modal } from "@mantine/core";
import InfoCard from "../InfoCard/InfoCard";

const ChatMessage = ({ message }) => {
  const [imageModalOpened, setImageModalOpened] = useState(false);
  const [imageHovered, setImageHovered] = useState(false);

  if (message.type === "user") {
    return (
      <>
        <Group
          justify="flex-end"
          align="flex-end"
          gap="md"
          style={{ animation: "fadeIn 0.3s" }}
        >
          <Box style={{ maxWidth: "85%", textAlign: "right" }}>
            <Paper
              p="md"
              radius="lg"
              style={{
                borderTopRightRadius: 0,
                backgroundColor: "var(--neutral-900)",
                color: "white",
              }}
              shadow="sm"
            >
              {/* Text content */}
              {message.content && (
                <Text
                  size="sm"
                  style={{
                    lineHeight: 1.6,
                    marginBottom: message.imageUrl ? "8px" : 0,
                  }}
                >
                  {message.content}
                </Text>
              )}

              {/* Image thumbnail */}
              {message.imageUrl && (
                <Box
                  style={{
                    cursor: "pointer",
                    borderRadius: "8px",
                    overflow: "hidden",
                    maxWidth: "200px",
                    marginLeft: "auto",
                    border: "2px solid rgba(255, 255, 255, 0.2)",
                    boxShadow: "0 2px 8px rgba(0, 0, 0, 0.15)",
                    transition: "all 0.2s ease",
                    position: "relative", // Added for the overlay
                  }}
                  onClick={() => setImageModalOpened(true)}
                  onMouseEnter={(e) => {
                    setImageHovered(true);
                    e.currentTarget.style.transform = "scale(1.02)";
                    e.currentTarget.style.boxShadow =
                      "0 4px 12px rgba(0, 0, 0, 0.25)";
                  }}
                  onMouseLeave={(e) => {
                    setImageHovered(false);
                    e.currentTarget.style.transform = "scale(1)";
                    e.currentTarget.style.boxShadow =
                      "0 2px 8px rgba(0, 0, 0, 0.15)";
                  }}
                >
                  <Image
                    src={message.imageUrl}
                    alt="Uploaded image"
                    fit="cover"
                    style={{
                      width: "100%",
                      height: "auto",
                      display: "block",
                    }}
                  />
                  {imageHovered && (
                    <Box
                      style={{
                        position: "absolute",
                        top: "4px",
                        right: "4px",
                        backgroundColor: "rgba(0, 0, 0, 0.7)",
                        color: "white",
                        padding: "4px 8px",
                        borderRadius: "4px",
                        fontSize: "11px",
                        fontWeight: "500",
                        animation: "fadeIn 0.2s",
                      }}
                    >
                      🔍 Click để phóng to
                    </Box>
                  )}
                </Box>
              )}
            </Paper>
            {message.status && (
              <Text size="xs" c="dimmed" mt={4} mr={4}>
                {message.status} {message.timestamp}
              </Text>
            )}
          </Box>
        </Group>

        {/* Image zoom modal */}
        <Modal
          opened={imageModalOpened}
          onClose={() => setImageModalOpened(false)}
          size="auto"
          centered
          padding="lg"
          withCloseButton
          zIndex={9999}
          styles={{
            body: {
              padding: "0",
              backgroundColor: "#000",
            },
            content: {
              maxWidth: "90vw",
              maxHeight: "90vh",
            },
            inner: {
              zIndex: 9999,
            },
            overlay: {
              zIndex: 9998,
            },
          }}
        >
          <Box
            style={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              backgroundColor: "#000",
              padding: "20px",
            }}
          >
            <Image
              src={message.imageUrl}
              alt="Zoomed image"
              fit="contain"
              style={{
                maxWidth: "100%",
                maxHeight: "calc(90vh - 80px)",
                objectFit: "contain",
              }}
            />
          </Box>
        </Modal>
      </>
    );
  }

  if (message.type === "assistant" || message.type === "ai") {
    return (
      <Group align="flex-start" gap="md" style={{ animation: "fadeIn 0.3s" }}>
        {/* Avatar */}
        <Avatar
          size="md"
          radius="xl"
          style={{
            border: "1px solid var(--mantine-color-gray-3)",
            backgroundColor: "var(--mantine-color-blue-6)",
            color: "white",
          }}
        >
          🤖
        </Avatar>

        {/* Message Content */}
        <Box style={{ maxWidth: "85%", flex: 1 }}>
          <Text size="xs" c="dimmed" ml={4} mb={4}>
            LocalMate AI
          </Text>

          <Paper
            p="md"
            radius="lg"
            style={{
              borderTopLeftRadius: 0,
              backgroundColor: "var(--mantine-color-gray-1)",
            }}
            shadow="sm"
          >
            <Box>
              {message.isLoading ? (
                <Box
                  style={{ display: "flex", alignItems: "center", gap: "6px" }}
                >
                  <Text size="sm" style={{ lineHeight: 1.6 }}>
                    {message.content}
                  </Text>
                  <Box
                    style={{
                      display: "inline-flex",
                      gap: "4px",
                      animation: "pulse 1.5s ease-in-out infinite",
                    }}
                  >
                    <span
                      style={{
                        width: "6px",
                        height: "6px",
                        borderRadius: "50%",
                        backgroundColor: "var(--mantine-color-blue-6)",
                        animation: "bounce 1.4s infinite ease-in-out both",
                        animationDelay: "-0.32s",
                      }}
                    />
                    <span
                      style={{
                        width: "6px",
                        height: "6px",
                        borderRadius: "50%",
                        backgroundColor: "var(--mantine-color-blue-6)",
                        animation: "bounce 1.4s infinite ease-in-out both",
                        animationDelay: "-0.16s",
                      }}
                    />
                    <span
                      style={{
                        width: "6px",
                        height: "6px",
                        borderRadius: "50%",
                        backgroundColor: "var(--mantine-color-blue-6)",
                        animation: "bounce 1.4s infinite ease-in-out both",
                      }}
                    />
                  </Box>
                </Box>
              ) : (
                <Text
                  size="sm"
                  style={{ lineHeight: 1.6 }}
                  dangerouslySetInnerHTML={{
                    __html: message.content
                      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
                      .replace(/\n/g, "<br />"),
                  }}
                />
              )}

              {/* Workflow info if available */}
              {message.workflow && (
                <Box
                  mt="sm"
                  p="xs"
                  style={{
                    backgroundColor: "var(--mantine-color-gray-0)",
                    borderRadius: "4px",
                    fontSize: "0.75rem",
                  }}
                >
                  <Text size="xs" c="dimmed">
                    🔧 Tools:{" "}
                    {message.workflow.tools_used?.join(", ") ||
                      message.toolsUsed?.join(", ") ||
                      "N/A"}
                  </Text>
                </Box>
              )}
            </Box>
          </Paper>
        </Box>
      </Group>
    );
  }

  // Handle system/error messages
  if (message.type === "system") {
    return (
      <Box style={{ textAlign: "center", padding: "8px 0" }}>
        <Text
          size="sm"
          c={message.isError ? "red" : "dimmed"}
          style={{
            fontStyle: "italic",
            backgroundColor: message.isError
              ? "var(--mantine-color-red-0)"
              : "transparent",
            padding: message.isError ? "8px 12px" : "0",
            borderRadius: message.isError ? "4px" : "0",
          }}
        >
          {message.content}
        </Text>
      </Box>
    );
  }

  return null;
};

export default ChatMessage;
