import React from "react";
import {
  Container,
  Title,
  Text,
  Grid,
  Paper,
  Stack,
  Box,
  TextInput,
  ActionIcon,
  ScrollArea,
  Card,
  Group,
} from "@mantine/core";
import {
  IconSend,
  IconBrain,
  IconLanguage,
  IconCalendar,
} from "@tabler/icons-react";

const ChatDemo = () => {
  const features = [
    {
      icon: <IconBrain size={24} />,
      color: "violet",
      title: "Smart Context Awareness",
      description:
        "It knows if it's raining in Ba Na Hills or if the Dragon Bridge is about to breathe fire, adjusting your plans instantly.",
    },
    {
      icon: <IconLanguage size={24} />,
      color: "orange",
      title: "Real-time Translation & Culture",
      description:
        "Break language barriers. Drivers use it to explain history in English, and tourists use it to order local food like a pro.",
    },
    {
      icon: <IconCalendar size={24} />,
      color: "teal",
      title: "Seamless Booking",
      description:
        "Integrated with local services. Find a spot, like it, and book a ride or ticket in one tap.",
    },
  ];

  return (
    <Box className="py-24 bg-gray-50 relative overflow-hidden">
      <Container size="xl" className="relative z-10">
        <Grid gutter="xl" align="center">
          <Grid.Col span={{ base: 12, lg: 5 }} order={{ base: 2, lg: 1 }}>
            <Paper
              shadow="xl"
              radius="xl"
              className="border border-gray-200 overflow-hidden transform hover:-translate-y-1 transition-transform duration-300"
            >
              <Box className="bg-gray-100 p-4 border-b border-gray-200 flex items-center space-x-3">
                <div className="flex space-x-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-400"></div>
                  <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
                  <div className="w-3 h-3 rounded-full bg-green-400"></div>
                </div>
                <Text
                  size="xs"
                  fw={500}
                  c="dimmed"
                  className="uppercase tracking-wider flex-1 text-center"
                >
                  Super Agent Chat
                </Text>
              </Box>

              <ScrollArea h={400} p="lg">
                <Stack gap="lg">
                  {/* User Message */}
                  <Group justify="flex-end" gap="xs">
                    <Paper
                      p="sm"
                      radius="lg"
                      className="bg-teal-500  max-w-[80%] shadow-md"
                      style={{ borderTopRightRadius: 0 }}
                    >
                      <Text size="sm">
                        I have 4 hours in Da Nang before my flight. What should
                        I do? 🕒
                      </Text>
                    </Paper>
                    <Box className="w-8 h-8 rounded-full bg-gray-200 flex-shrink-0 overflow-hidden">
                      <img
                        src="https://lh3.googleusercontent.com/aida-public/AB6AXuCBM-34NPqt1l42ixg9EmYwaLL4MtuHNa9dlu4PsKoDH9703RKH0Y__BFEu3vQK_ZPYKfXqo2cziArXiQp3SR6upSvbONXMiEFH1q9LkyukmcBgPEaWEtj4YHZdFK2yn2-r5SB70dShiQqmGMLWbLsVtkZAEZYYd2ZcKxWXPS-7iDHZ9jI77sgcOuLXz8pH9rUo1pyPbN5CW1-TEesVqj7OUsgcPHfQmNBE6FLIs2zHv_qd1hiqYZH66StvRVTOXjXJNgreKl2c0XZN"
                        alt="User"
                        className="w-full h-full object-cover"
                      />
                    </Box>
                  </Group>

                  {/* AI Response */}
                  <Group align="flex-start" gap="xs">
                    <Box className="w-8 h-8 rounded-lg bg-gradient-to-br from-teal-500 to-blue-500 flex-shrink-0 flex items-center justify-center text-white text-xs font-bold">
                      AI
                    </Box>
                    <Stack gap="sm" className="max-w-[85%]">
                      <Paper
                        p="sm"
                        radius="lg"
                        className="bg-gray-100 shadow-sm"
                        style={{ borderTopLeftRadius: 0 }}
                      >
                        <Text size="sm">
                          With 4 hours, I recommend staying close to the city
                          center. Here is a perfect mini-itinerary:
                        </Text>
                      </Paper>

                      <Card
                        padding="sm"
                        radius="lg"
                        className="border border-gray-200 shadow-sm"
                      >
                        <img
                          src="https://lh3.googleusercontent.com/aida-public/AB6AXuDsP5c7wu20GCdx9lCJ6ZgGrK4tKfhHuLdsLmzvBklSqJ5MhLYsqkd_9BpyaJy9xi6Vz-4xRMCmRximpyxvaIHZ6bB5E0c3BOV21QZuxlBIfTKP0sCnG2MFpVl3u2lKLX-Y6BnmjXhXIN_8lg8CWHU2RWBb3ONhGfoRjh1Hdr0PXsKjQUbmG4OwxYayc5JX-rDx9XNTpdw8XokWxj4_zPmBZwN7aQxH3VZdpiaNJqnde4HBFpzsB_bA2vDEefVQeulC0PkMSpLeNpsJ"
                          alt="Dragon Bridge"
                          className="w-full h-32 object-cover rounded-lg mb-2"
                        />
                        <Title order={6} size="sm" className="font-bold">
                          1. Dragon Bridge & Love Lock Bridge
                        </Title>
                        <Text size="xs" c="dimmed" mt={4}>
                          Iconic photo spots. 30 mins.
                        </Text>
                      </Card>

                      <Paper
                        p="sm"
                        radius="lg"
                        className="bg-gray-100 shadow-sm"
                      >
                        <Text size="sm">
                          Would you like me to book a Grab directly to the
                          Dragon Bridge?
                        </Text>
                      </Paper>
                    </Stack>
                  </Group>
                </Stack>
              </ScrollArea>

              <Box className="p-4 bg-gray-50 border-t border-gray-200">
                <div className="relative">
                  <TextInput
                    placeholder="Ask anything about Da Nang..."
                    radius="xl"
                    size="md"
                    rightSection={
                      <ActionIcon
                        size={32}
                        radius="xl"
                        variant="filled"
                        className="bg-teal-500 hover:bg-teal-600"
                      >
                        <IconSend size={16} />
                      </ActionIcon>
                    }
                  />
                </div>
              </Box>
            </Paper>
          </Grid.Col>

          <Grid.Col
            span={{ base: 12, lg: 7 }}
            order={{ base: 1, lg: 2 }}
            pl={{ lg: "xl" }}
          >
            <Title order={1} className="text-3xl lg:text-4xl font-bold mb-6">
              More Than Just a Chatbot. <br />
              <span className="text-teal-600">A Complete Travel Ecology.</span>
            </Title>
            <br />
            <Text size="lg" c="dimmed" className="mb-8">
              The Danang Super Agent connects the dots. It doesn't just give you
              a list; it understands context, weather, traffic, and your
              personal preferences to build a live, actionable plan.
            </Text>
            <br />
            <Stack gap="xl">
              {features.map((feature, idx) => (
                <Group key={idx} align="flex-start">
                  <Box
                    className={`flex items-center justify-center h-12 w-12 rounded-xl bg-${feature.color}-50 text-${feature.color}-600`}
                    style={{
                      backgroundColor: `var(--mantine-color-${feature.color}-0)`,
                      color: `var(--mantine-color-${feature.color}-6)`,
                    }}
                  >
                    {feature.icon}
                  </Box>
                  <Box style={{ flex: 1 }}>
                    <Title order={4} size="xl" className="font-semibold mb-2">
                      {feature.title}
                    </Title>
                    <Text size="sm" c="dimmed">
                      {feature.description}
                    </Text>
                  </Box>
                </Group>
              ))}
            </Stack>
          </Grid.Col>
        </Grid>
      </Container>
    </Box>
  );
};

export default ChatDemo;
