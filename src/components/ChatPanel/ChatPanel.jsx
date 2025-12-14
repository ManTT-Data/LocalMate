import React from "react";
import { Box, Stack, ScrollArea } from "@mantine/core";
import ChatMessage from "../../components/ChatMessage/ChatMessage";
import DateSeparator from "../DateSeparator/DateSeparator";
import MessageComposer from "../MessageComposer/MessageComposer";
import { chatMessages } from "../../data/mockData";

const ChatPanel = ({ onSendMessage }) => {
  return (
    <Box
      w={{ base: "100%", md: 420, lg: 480 }}
      style={{
        display: "flex",
        flexDirection: "column",
        borderRight: "1px solid var(--mantine-color-gray-3)",
        backgroundColor: "white",
        position: "relative",
        flexShrink: 0,
      }}
    >
      {/* Chat History */}
      <ScrollArea flex={1} p="md">
        <Stack gap="xl">
          {chatMessages.map((message) => {
            if (message.type === "date-separator") {
              return <DateSeparator key={message.id} date={message.content} />;
            }
            return <ChatMessage key={message.id} message={message} />;
          })}
        </Stack>
      </ScrollArea>

      {/* Message Composer */}
      <MessageComposer onSendMessage={onSendMessage} />
    </Box>
  );
};

export default ChatPanel;
