import React, { useEffect, useState } from "react";
import {
  Modal,
  Text,
  Card,
  Stack,
  Group,
  Badge,
  Loader,
  Alert,
  ScrollArea,
  ActionIcon,
  Divider,
  Box,
  Title,
} from "@mantine/core";
import {
  IconMessageCircle,
  IconAlertCircle,
  IconTrash,
  IconClock,
} from "@tabler/icons-react";
import { getChatHistory } from "../apis/aiService";
import useAuthStore from "../stores/useAuthStore";

/**
 * HistoryModal - Display chat history for the current user
 * @param {boolean} opened - Whether the modal is opened
 * @param {function} onClose - Callback when modal is closed
 */
const HistoryModal = ({ opened, onClose }) => {
  const [historyData, setHistoryData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { getUserId } = useAuthStore();

  // Fetch chat history when modal opens
  useEffect(() => {
    if (opened) {
      fetchHistory();
    }
  }, [opened]);

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);

    try {
      const userId = getUserId();
      const response = await getChatHistory(userId);
      setHistoryData(response);
    } catch (err) {
      console.error("Failed to fetch chat history:", err);
      setError(err.message || "Failed to load chat history");
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (timestamp) => {
    if (!timestamp) return "Unknown";
    const date = new Date(timestamp);
    return date.toLocaleString("vi-VN", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <Modal
      opened={opened}
      onClose={onClose}
      title={
        <Group gap="xs">
          <IconMessageCircle size={24} />
          <Title order={3}>Chat History</Title>
        </Group>
      }
      size="lg"
      centered
      scrollAreaComponent={ScrollArea.Autosize}
    >
      <Stack gap="md">
        {loading && (
          <Group justify="center" py="xl">
            <Loader size="lg" />
            <Text c="dimmed">Loading history...</Text>
          </Group>
        )}

        {error && (
          <Alert
            icon={<IconAlertCircle size={16} />}
            title="Error"
            color="red"
            variant="filled"
          >
            {error}
          </Alert>
        )}

        {!loading && !error && historyData && (
          <>
            {/* Summary Section */}
            <Card withBorder p="md" radius="md">
              <Stack gap="xs">
                <Group justify="space-between">
                  <Text fw={600} size="sm">
                    Summary
                  </Text>
                  <Badge color="blue" variant="light">
                    {historyData.sessions?.length || 0} Sessions
                  </Badge>
                </Group>
                <Divider />
                <Group gap="xl">
                  <Box>
                    <Text size="xs" c="dimmed">
                      Current Session
                    </Text>
                    <Text fw={500} size="sm">
                      {historyData.current_session || "default"}
                    </Text>
                  </Box>
                  <Box>
                    <Text size="xs" c="dimmed">
                      Total Messages
                    </Text>
                    <Text fw={500} size="sm">
                      {historyData.total_messages || 0}
                    </Text>
                  </Box>
                </Group>
              </Stack>
            </Card>

            {/* Sessions List */}
            <Stack gap="sm">
              <Text fw={600} size="sm">
                All Sessions
              </Text>

              {historyData.sessions && historyData.sessions.length > 0 ? (
                <ScrollArea.Autosize mah={400}>
                  <Stack gap="xs">
                    {historyData.sessions.map((session, index) => (
                      <Card
                        key={index}
                        withBorder
                        p="md"
                        radius="md"
                        style={{
                          cursor: "pointer",
                          transition: "all 0.2s ease",
                          backgroundColor:
                            session === historyData.current_session
                              ? "var(--mantine-color-blue-0)"
                              : "white",
                        }}
                        onMouseEnter={(e) => {
                          if (session !== historyData.current_session) {
                            e.currentTarget.style.backgroundColor =
                              "var(--mantine-color-gray-0)";
                          }
                        }}
                        onMouseLeave={(e) => {
                          if (session !== historyData.current_session) {
                            e.currentTarget.style.backgroundColor = "white";
                          }
                        }}
                      >
                        <Group justify="space-between">
                          <Group gap="sm">
                            <IconMessageCircle
                              size={20}
                              style={{
                                color:
                                  session === historyData.current_session
                                    ? "var(--mantine-color-blue-6)"
                                    : "var(--mantine-color-gray-6)",
                              }}
                            />
                            <Stack gap={2}>
                              <Text fw={500} size="sm">
                                {session}
                              </Text>
                              <Group gap="xs">
                                <IconClock size={12} />
                                <Text size="xs" c="dimmed">
                                  Session ID
                                </Text>
                              </Group>
                            </Stack>
                          </Group>

                          <Group gap="xs">
                            {session === historyData.current_session && (
                              <Badge color="blue" variant="filled" size="sm">
                                Active
                              </Badge>
                            )}
                            {session !== historyData.current_session && (
                              <ActionIcon
                                variant="subtle"
                                color="red"
                                size="sm"
                                radius="xl"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  // TODO: Implement delete session functionality
                                  console.log("Delete session:", session);
                                }}
                              >
                                <IconTrash size={16} />
                              </ActionIcon>
                            )}
                          </Group>
                        </Group>
                      </Card>
                    ))}
                  </Stack>
                </ScrollArea.Autosize>
              ) : (
                <Card withBorder p="xl" radius="md">
                  <Stack align="center" gap="xs">
                    <IconMessageCircle size={48} stroke={1} color="gray" />
                    <Text c="dimmed" size="sm">
                      No chat sessions found
                    </Text>
                  </Stack>
                </Card>
              )}
            </Stack>

            {/* Additional Info */}
            {historyData.last_updated && (
              <Group justify="center" mt="md">
                <Text size="xs" c="dimmed">
                  Last updated: {formatDate(historyData.last_updated)}
                </Text>
              </Group>
            )}
          </>
        )}
      </Stack>
    </Modal>
  );
};

export default HistoryModal;
