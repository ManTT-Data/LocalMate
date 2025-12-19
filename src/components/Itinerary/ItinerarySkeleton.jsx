import React from "react";
import { Box, Paper, Skeleton, Flex, Group, Card } from "@mantine/core";

const ItinerarySkeleton = () => {
    return (
        <Box p="md" className="custom-scrollbar" style={{ overflow: "hidden" }}>
            {/* Header Skeleton */}
            <Box mb="xl" px="sm">
                <Skeleton h={28} w="60%" mb="xs" radius="xl" />
                <Skeleton h={14} w="40%" radius="xl" />
            </Box>

            {/* Days Skeleton */}
            {[1, 2].map((day) => (
                <Box key={day} mb="xl">
                    {/* Day Header Skeleton */}
                    <Paper p="md" radius="lg" mb="sm" withBorder>
                        <Flex justify="space-between" align="center">
                            <Group gap="sm">
                                <Skeleton h={32} w={80} radius="md" />
                                <Skeleton h={20} w={120} radius="xl" />
                            </Group>
                            <Skeleton h={24} w={40} radius="xl" />
                        </Flex>
                    </Paper>

                    {/* Stops Skeleton */}
                    <Box pos="relative" ml="xs" pl={32}>
                        {/* Timeline Line */}
                        <Box
                            pos="absolute"
                            left={7}
                            top={0}
                            bottom={0}
                            w={2}
                            bg="gray.1"
                        />

                        {[1, 2].map((stop) => (
                            <Box key={stop} mb="md" pos="relative">
                                {/* Dot */}
                                <Box
                                    pos="absolute"
                                    left={-32 + 7 - 10}
                                    top={10}
                                    style={{ zIndex: 10 }}
                                >
                                    <Skeleton h={20} w={20} circle />
                                </Box>

                                <Paper p="sm" radius="md" withBorder>
                                    <Flex gap="md" align="center">
                                        <Skeleton h={56} w={56} radius="md" />
                                        <Box flex={1}>
                                            <Skeleton h={16} w="70%" mb="xs" radius="xl" />
                                            <Skeleton h={12} w="40%" radius="xl" />
                                        </Box>
                                    </Flex>
                                </Paper>
                            </Box>
                        ))}
                    </Box>
                </Box>
            ))}

            {/* Footer Button Skeleton */}
            <Box p="md" mt="xl">
                <Skeleton h={48} w="100%" radius="xl" />
            </Box>
        </Box>
    );
};

export default ItinerarySkeleton;
