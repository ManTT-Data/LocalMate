import React, { useState, useEffect, useRef } from "react";
import {
  Box,
  Stack,
  ScrollArea,
  Center,
  Loader,
  Text,
  Group,
  Button,
  ActionIcon,
  Tooltip,
  Divider,
} from "@mantine/core";
import { IconBrain, IconTrash, IconSparkles } from "@tabler/icons-react";
import ChatMessage from "../../components/ChatMessage/ChatMessage";
import DateSeparator from "../DateSeparator/DateSeparator";
import MessageComposer from "../MessageComposer/MessageComposer";
import PlaceCard from "../PlaceCard/PlaceCard";
import {
  uploadImage,
  sendMessage,
  getChatHistory,
  clearConversation,
  searchByImage,
} from "../../apis/aiService";
import useItineraryStore from "../../stores/useItineraryStore";
import useAiPlacesStore from "../../stores/useAiPlacesStore";
import { getCurrentUserId, getCurrentSessionId } from "../../utils/authHelpers";

const ChatPanel = ({
  onSendMessage,
  userId = getCurrentUserId(),
  sessionId = getCurrentSessionId(),
}) => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState(null);
  const [reactMode, setReactMode] = useState(false);
  const scrollAreaRef = useRef(null);
  const viewport = useRef(null);

  // Get itinerary store for adding places to plan
  const { addItem, plan } = useItineraryStore();

  // Get AI places store for sharing with map
  const { setAiPlaces } = useAiPlacesStore();

  // LocalStorage helpers
  const getLocalStorageKey = () => `chat_${userId}_${sessionId}`;

  const saveToLocalStorage = (messages) => {
    try {
      const key = getLocalStorageKey();
      localStorage.setItem(key, JSON.stringify(messages));
    } catch (error) {
      console.error("Error saving to localStorage:", error);
    }
  };

  const loadFromLocalStorage = () => {
    try {
      const key = getLocalStorageKey();
      const stored = localStorage.getItem(key);
      return stored ? JSON.parse(stored) : null;
    } catch (error) {
      console.error("Error loading from localStorage:", error);
      return null;
    }
  };

  // Fetch chat history on mount
  useEffect(() => {
    const fetchChatHistory = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Try to load from localStorage first for instant display
        const cachedMessages = loadFromLocalStorage();
        if (cachedMessages && cachedMessages.length > 0) {
          setMessages(cachedMessages);
          console.log(
            "📦 Loaded",
            cachedMessages.length,
            "messages from localStorage"
          );
        }

        // Fetch chat history from backend
        const response = await getChatHistory(userId);

        // Backend returns: { user_id, sessions, current_session, message_count }
        // The backend may also return messages array if available
        if (response?.messages && Array.isArray(response.messages)) {
          // Transform backend messages to UI format
          const transformedMessages = response.messages.map((msg, idx) => ({
            id: `${msg.role}-${msg.timestamp || idx}`,
            type: msg.role === "user" ? "user" : "assistant",
            content: msg.content || msg.message || "",
            timestamp: msg.timestamp || new Date().toISOString(),
            ...(msg.places && { places: msg.places }),
            ...(msg.workflow && { workflow: msg.workflow }),
            ...(msg.tools_used && { toolsUsed: msg.tools_used }),
            ...(msg.image_url && { imageUrl: msg.image_url }),
          }));

          setMessages(transformedMessages);
          saveToLocalStorage(transformedMessages);
          console.log(
            "✅ Loaded",
            transformedMessages.length,
            "messages from backend"
          );
        } else {
          // If backend doesn't return messages, keep localStorage cache
          console.log(
            "ℹ️ Backend returned no messages, using localStorage cache"
          );

          // If no cached messages, show welcome message
          if (!cachedMessages || cachedMessages.length === 0) {
            const welcomeMessage = {
              id: "welcome-message",
              type: "assistant",
              content: `Xin chào! 👋 Tôi là trợ lý AI của **LocalMate** - người bạn đồng hành du lịch Đà Nẵng của bạn!\n\nTôi có thể giúp bạn:\n\n🍜 **Tìm kiếm địa điểm**: Quán ăn, cafe, điểm tham quan, khách sạn...\n📍 **Gợi ý lộ trình**: Lên kế hoạch chi tiết cho chuyến đi\n🖼️ **Tìm theo hình ảnh**: Upload ảnh để tìm địa điểm tương tự\n⭐ **Đánh giá chất lượng**: Xem rating và review thực tế\n\nHãy bắt đầu bằng cách cho tôi biết bạn đang tìm kiếm gì nhé! Ví dụ: "*Quán cafe view đẹp gần Mỹ Khê*" hoặc "*Món ăn đặc sản Đà Nẵng*" 🌟`,
              timestamp: new Date().toISOString(),
            };
            setMessages([welcomeMessage]);
            saveToLocalStorage([welcomeMessage]);
          }
        }
      } catch (error) {
        console.error("Error fetching chat history:", error);
        setError(error.message);

        // Fall back to localStorage if backend fails
        const cachedMessages = loadFromLocalStorage();
        if (cachedMessages && cachedMessages.length > 0) {
          setMessages(cachedMessages);
          console.log("⚠️ Backend failed, using localStorage cache");
        } else {
          // Show welcome message when no history available
          const welcomeMessage = {
            id: "welcome-message",
            type: "assistant",
            content: `Xin chào! 👋 Tôi là trợ lý AI của **LocalMate** - người bạn đồng hành du lịch Đà Nẵng của bạn!\n\nTôi có thể giúp bạn:\n\n🍜 **Tìm kiếm địa điểm**: Quán ăn, cafe, điểm tham quan, khách sạn...\n📍 **Gợi ý lộ trình**: Lên kế hoạch chi tiết cho chuyến đi\n🖼️ **Tìm theo hình ảnh**: Upload ảnh để tìm địa điểm tương tự\n⭐ **Đánh giá chất lượng**: Xem rating và review thực tế\n\nHãy bắt đầu bằng cách cho tôi biết bạn đang tìm kiếm gì nhé! Ví dụ: "*Quán cafe view đẹp gần Mỹ Khê*" hoặc "*Món ăn đặc sản Đà Nẵng*" 🌟`,
            timestamp: new Date().toISOString(),
          };
          setMessages([welcomeMessage]);
          saveToLocalStorage([welcomeMessage]);
        }
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

  // Check if place is already in plan
  const isPlaceInPlan = (placeId) => {
    return plan.items.some(
      (item) => item.place_id === placeId || item.placeId === placeId
    );
  };

  // Handle adding place to plan
  const handleAddToPlan = (place) => {
    addItem(place);
  };

  // Handle clearing conversation
  const handleClearConversation = async () => {
    if (!window.confirm("Clear entire chat history?")) return;

    try {
      await clearConversation(userId, sessionId);
      setMessages([]);
      // Clear localStorage cache
      const key = getLocalStorageKey();
      localStorage.removeItem(key);
      console.log("🗑️ Cleared chat history and localStorage");
    } catch (error) {
      console.error("Error clearing conversation:", error);
    }
  };

  // Toggle ReAct mode
  const handleToggleReactMode = () => {
    setReactMode(!reactMode);
  };

  // Handle sending a message
  const handleSendMessage = async (messageText, imageFile = null) => {
    if (!messageText.trim() && !imageFile) return;

    try {
      setIsSending(true);

      // Log test user info for debugging
      console.log("📤 Sending message with credentials:", {
        userId,
        sessionId,
        messagePreview: messageText?.substring(0, 50) + "...",
        hasImage: !!imageFile,
      });

      // Add user message to UI immediately (optimistic update)
      let imageUrl = null;
      let uploadedImageUrl = null;

      // If there's an image, upload to Supabase first
      if (imageFile) {
        try {
          console.log("📤 Uploading image to Supabase...");
          const uploadResult = await uploadImage(imageFile, userId);
          uploadedImageUrl = uploadResult.url;
          imageUrl = uploadedImageUrl; // Use Supabase URL for display
          console.log("✅ Image uploaded:", uploadResult);
        } catch (error) {
          console.error("❌ Image upload failed:", error);
          // Fallback to base64 for preview if upload fails
          imageUrl = await fileToBase64(imageFile);
        }
      }

      const userMessage = {
        id: `user-${Date.now()}`,
        type: "user",
        content: messageText || "",
        timestamp: new Date().toISOString(),
        imageUrl: imageUrl,
      };
      setMessages((prev) => {
        const updated = [...prev, userMessage];
        saveToLocalStorage(updated);
        return updated;
      });

      // Add loading message
      const loadingMessage = {
        id: `loading-${Date.now()}`,
        type: "assistant",
        content: imageFile ? "Đang phân tích ảnh..." : "Đang suy nghĩ...",
        timestamp: new Date().toISOString(),
        isLoading: true,
      };
      setMessages((prev) => [...prev, loadingMessage]);

      let response;

      // If there's an image, handle image search with Supabase URL
      if (imageFile && uploadedImageUrl) {
        try {
          // Send with Supabase image URL
          response = await sendMessage({
            message: messageText || "Tìm địa điểm tương tự ảnh này",
            userId,
            sessionId,
            provider: "MegaLLM",
            reactMode: reactMode,
            imageUrl: uploadedImageUrl, // Use Supabase URL
          });
        } catch (error) {
          console.error("Image search error:", error);
          throw error;
        }
      } else {
        // Regular text message
        response = await sendMessage({
          message: messageText,
          userId,
          sessionId,
          provider: "MegaLLM",
          reactMode: reactMode,
        });
      }

      // Remove loading message
      setMessages((prev) => prev.filter((msg) => msg.id !== loadingMessage.id));

      // Log the full response for debugging
      console.log("📨 Send Message Response:", response);
      console.log("📍 Places in response:", response?.places);

      // Add assistant response to UI with places from API
      if (response?.response) {
        // Use places directly from API response
        const places = response.places || [];

        // Update AI places store for map integration
        if (places.length > 0) {
          setAiPlaces(places);
        }

        const assistantMessage = {
          id: `assistant-${Date.now()}`,
          type: "assistant",
          content: response.response,
          timestamp: new Date().toISOString(),
          workflow: response.workflow,
          toolsUsed: response.tools_used,
          places: places, // Attach places from API
        };
        setMessages((prev) => {
          const updated = [...prev, assistantMessage];
          saveToLocalStorage(updated);
          return updated;
        });
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
      setMessages((prev) => {
        const updated = [...prev, errorMessage];
        saveToLocalStorage(updated);
        return updated;
      });
    } finally {
      setIsSending(false);
    }
  };

  // Convert file to base64
  const fileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
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
      {/* Chat Controls Header */}
      <Box
        p="sm"
        style={{
          borderBottom: "1px solid var(--mantine-color-gray-3)",
          backgroundColor: "var(--mantine-color-gray-0)",
        }}
      >
        <Group justify="space-between" gap="xs">
          <Group gap="xs">
            <Tooltip
              label={
                reactMode
                  ? "ReAct mode: Multi-step reasoning enabled"
                  : "ReAct mode: Single-step response"
              }
            >
              <Button
                size="xs"
                variant={reactMode ? "filled" : "light"}
                color={reactMode ? "blue" : "gray"}
                leftSection={<IconBrain size={16} />}
                onClick={handleToggleReactMode}
                styles={{
                  root: {
                    transition: "all 0.2s",
                  },
                }}
              >
                {reactMode ? "ReAct: ON" : "ReAct: OFF"}
              </Button>
            </Tooltip>
          </Group>

          <Tooltip label="Clear conversation history">
            <ActionIcon
              variant="subtle"
              color="red"
              size="lg"
              onClick={handleClearConversation}
              disabled={messages.length === 0}
            >
              <IconTrash size={18} />
            </ActionIcon>
          </Tooltip>
        </Group>
      </Box>
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

              return (
                <Box key={message.id}>
                  <ChatMessage message={message} />

                  {/* Display place cards if available */}
                  {message.places && message.places.length > 0 && (
                    <Stack gap="xs" mt="md">
                      {message.places.map((place) => (
                        <PlaceCard
                          key={place.place_id}
                          place={place}
                          onAddToPlan={handleAddToPlan}
                          isAdded={isPlaceInPlan(place.place_id)}
                        />
                      ))}
                    </Stack>
                  )}
                </Box>
              );
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
