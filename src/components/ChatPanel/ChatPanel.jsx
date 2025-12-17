import React, { useState, useEffect, useRef } from "react";
import { Box, Stack, ScrollArea, Center, Loader, Text } from "@mantine/core";
import ChatMessage from "../../components/ChatMessage/ChatMessage";
import DateSeparator from "../DateSeparator/DateSeparator";
import MessageComposer from "../MessageComposer/MessageComposer";
import { sendMessage, getChatHistory } from "../../apis/aiService";

const ChatPanel = ({
  onSendMessage,
  userId = "anonymous",
  sessionId = "default",
}) => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState(null);
  const scrollAreaRef = useRef(null);
  const viewport = useRef(null);

  // Fetch chat history on mount
  useEffect(() => {
    const fetchChatHistory = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Fetch chat history from backend
        const response = await getChatHistory(userId);

        // Transform backend messages to UI format
        // Backend returns: { user_id, sessions, current_session, message_count }
        // For now, we'll start with an empty array and messages will populate as user chats
        setMessages([]);
      } catch (error) {
        console.error("Error fetching chat history:", error);
        setError(error.message);
        setMessages([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchChatHistory();
  }, [userId, sessionId]);

  // Scroll to bottom when messages change
  useEffect(() => {
    if (viewport.current) {
      viewport.current.scrollTo({
        top: viewport.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages]);

  // Handle sending a message
  const handleSendMessage = async (messageText, imageFile = null) => {
    if (!messageText.trim() && !imageFile) return;

    try {
      setIsSending(true);

      // Add user message to UI immediately (optimistic update)
      const userMessage = {
        id: `user-${Date.now()}`,
        type: "user",
        content: messageText,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);

      // Prepare message data for API
      const messageData = {
        message: messageText,
        userId,
        sessionId,
        provider: "MegaLLM", // or "Google" based on user preference
        reactMode: false,
      };

      // If there's an image, handle image search
      if (imageFile) {
        // TODO: Implement image search via searchByImage API
        console.log("Image search not yet implemented:", imageFile);
      }

      // Send message to backend
      const response = await sendMessage(messageData);

      // Add assistant response to UI
      if (response?.response) {
        const assistantMessage = {
          id: `assistant-${Date.now()}`,
          type: "assistant",
          content: response.response,
          timestamp: new Date().toISOString(),
          workflow: response.workflow, // Include workflow data for debugging
          toolsUsed: response.tools_used,
        };
        setMessages((prev) => [...prev, assistantMessage]);
      }

      // Call parent callback if provided
      if (onSendMessage) {
        onSendMessage(messageText, response);
      }
    } catch (error) {
      console.error("Error sending message:", error);

      // Add error message to UI
      const errorMessage = {
        id: `error-${Date.now()}`,
        type: "system",
        content: `Error: ${error.message}`,
        timestamp: new Date().toISOString(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsSending(false);
    }
  };

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
      <ScrollArea flex={1} p="md" viewportRef={viewport}>
        {isLoading ? (
          <Center h="100%">
            <Stack align="center" gap="sm">
              <Loader size="md" />
              <Text size="sm" c="dimmed">
                Loading chat history...
              </Text>
            </Stack>
          </Center>
        ) : error ? (
          <Center h="100%">
            <Text size="sm" c="red">
              Error loading chat: {error}
            </Text>
          </Center>
        ) : messages.length === 0 ? (
          <Center h="100%">
            <Text size="sm" c="dimmed">
              Start a conversation by sending a message below
            </Text>
          </Center>
        ) : (
          <Stack gap="xl">
            {messages.map((message) => {
              if (message.type === "date-separator") {
                return (
                  <DateSeparator key={message.id} date={message.content} />
                );
              }
              return <ChatMessage key={message.id} message={message} />;
            })}
          </Stack>
        )}
      </ScrollArea>

      {/* Message Composer */}
      <MessageComposer
        onSendMessage={handleSendMessage}
        disabled={isSending}
        loading={isSending}
      />
    </Box>
  );
};

export default ChatPanel;
