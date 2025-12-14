import React from "react";
import { Group, Box, Avatar, Text, Paper } from "@mantine/core";
import InfoCard from "../InfoCard/InfoCard";

const ChatMessage = ({ message }) => {
  if (message.type === "user") {
    return (
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
            <Text size="sm" style={{ lineHeight: 1.6 }}>
              {message.content}
            </Text>
          </Paper>
          {message.status && (
            <Text size="xs" c="dimmed" mt={4} mr={4}>
              {message.status} {message.timestamp}
            </Text>
          )}
        </Box>
      </Group>
    );
  }

  if (message.type === "ai") {
    return (
      <Group align="flex-end" gap="md" style={{ animation: "fadeIn 0.3s" }}>
        {/* Avatar */}
        <Avatar
          src={message.sender.avatar}
          alt={message.sender.name}
          size="md"
          radius="xl"
          style={{ border: "1px solid var(--mantine-color-gray-3)" }}
        />

        {/* Message Content */}
        <Box style={{ maxWidth: "90%" }}>
          <Text size="xs" c="dimmed" ml={4} mb={4}>
            {message.sender.name}
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
              <Text size="sm" style={{ lineHeight: 1.6 }}>
                {message.content}
              </Text>

              {/* Info Card if present */}
              {message.hasInfoCard && message.infoCard && (
                <Box mt="md">
                  <InfoCard data={message.infoCard} />
                </Box>
              )}

              {/* Additional text if present */}
              {message.additionalText && (
                <Text
                  size="sm"
                  mt="md"
                  dangerouslySetInnerHTML={{
                    __html: message.additionalText
                      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
                      .replace(/\n/g, "<br />"),
                  }}
                />
              )}
            </Box>
          </Paper>
        </Box>
      </Group>
    );
  }

  return null;
};

export default ChatMessage;
