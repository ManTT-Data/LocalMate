import React from "react";
import { Container, Title, Text, Button, Group, Box } from "@mantine/core";
import { IconDownload } from "@tabler/icons-react";

import { useNavigate } from "react-router-dom";

const CTASection = () => {
  const navigate = useNavigate();

  return (
    <Box className="py-20 mt-24">
      <Container size="lg">
        <Box
          className="rounded-3xl p-10 md:p-16 text-center relative overflow-hidden shadow-2xl"
          style={{
            background: "linear-gradient(135deg, #1f2937 0%, #111827 100%)",
          }}
        >
          <div
            className="absolute top-0 left-0 w-64 h-64 rounded-full blur-3xl opacity-30"
            style={{
              background: "rgba(20, 184, 166, 0.3)",
              transform: "translate(-50%, -50%)",
            }}
          />
          <div
            className="absolute bottom-0 right-0 w-64 h-64 rounded-full blur-3xl opacity-30"
            style={{
              background: "rgba(59, 130, 246, 0.3)",
              transform: "translate(50%, 50%)",
            }}
          />

          <div className="relative z-10 flex flex-col items-center justify-center">
            <Title
              order={1}
              c="white"
              className="text-3xl md:text-5xl font-bold mb-6 text-center"
              style={{ textShadow: "0 2px 10px rgba(0,0,0,0.2)" }}
            >
              Start Your Smart Journey Today
            </Title>

            <Text size="lg" c="gray.3" ta="center" className="mb-10 max-w-2xl">
              Whether you're driving the streets or walking them, let AI unlock
              the full potential of Da Nang for you.
            </Text>
            <br />
            <div className="flex flex-wrap justify-center gap-4">
              <Button
                size="lg"
                radius="xl"
                leftSection={<IconDownload size={20} />}
                className="bg-teal-500 hover:bg-teal-600"
                style={{
                  boxShadow: "0 10px 25px rgba(20, 184, 166, 0.4)",
                }}
              >
                Download App
              </Button>

              <Button
                size="lg"
                radius="xl"
                variant="outline"
                c="white"
                className="border-2 border-white/20 backdrop-blur-sm hover:bg-white/10"
                onClick={() => navigate("/map")}
              >
                Try Web Version
              </Button>
            </div>
          </div>
        </Box>
      </Container>
    </Box>
  );
};

export default CTASection;
