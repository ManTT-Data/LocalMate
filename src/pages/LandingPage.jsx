import React, { useEffect } from "react";
import { AppShell, Container, Group, Button, Box, Anchor } from "@mantine/core";

import { useNavigate } from "react-router-dom";
import HeroSection from "../components/Landing/HeroSection";
import FeaturesSection from "../components/Landing/FeaturesSection";
import ChatDemo from "../components/Landing/ChatDemo";
import DestinationsGrid from "../components/Landing/DestinationsGrid";
import CTASection from "../components/Landing/CTASection";
import LandingFooter from "../components/Landing/LandingFooter";

const LandingPage = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Enable scrolling for landing page
    document.documentElement.style.overflow = "auto";
    document.body.style.overflow = "auto";

    // Cleanup: restore overflow hidden when component unmounts
    return () => {
      document.documentElement.style.overflow = "hidden";
      document.body.style.overflow = "hidden";
    };
  }, []);

  return (
    <Box>
      {/* Fixed Navigation Bar */}
      <Box
        component="nav"
        className="fixed w-full z-50 bg-white/80 backdrop-blur-md border-b border-gray-100 dark:border-gray-800"
      >
        <Container size="xl">
          <Group justify="space-between" h={80}>
            {/* Logo */}
            <Group gap="sm">
              <Box className="w-8 h-8 rounded-lg bg-gradient-to-br from-teal-500 to-blue-500 flex items-center justify-center text-white font-bold text-lg">
                L
              </Box>
              <span className="font-bold text-xl tracking-tight">
                LocalMate<span className="text-teal-500"></span>
              </span>
            </Group>

            {/* Desktop Navigation */}
            <Group gap="xl" visibleFrom="md">
              <Anchor
                href="#features"
                c="dimmed"
                className="hover:text-teal-600 transition-colors text-sm font-medium"
              >
                Features
              </Anchor>
              <Anchor
                href="#drivers"
                c="dimmed"
                className="hover:text-teal-600 transition-colors text-sm font-medium"
              >
                For Drivers
              </Anchor>
              <Anchor
                href="#tourists"
                c="dimmed"
                className="hover:text-teal-600 transition-colors text-sm font-medium"
              >
                For Tourists
              </Anchor>
              <Anchor
                href="#destinations"
                c="dimmed"
                className="hover:text-teal-600 transition-colors text-sm font-medium"
              >
                Destinations
              </Anchor>
            </Group>

            {/* Right Section */}
            <Group gap="md">
              <Button
                radius="xl"
                className="bg-teal-500 hover:bg-teal-600"
                onClick={() => navigate("/login")}
                style={{
                  boxShadow: "0 4px 12px rgba(20, 184, 166, 0.3)",
                }}
              >
                Start Planning
              </Button>
            </Group>
          </Group>
        </Container>
      </Box>

      {/* Main Content */}
      <HeroSection />
      <FeaturesSection />
      <ChatDemo />
      <DestinationsGrid />
      <CTASection />
      <LandingFooter />
    </Box>
  );
};

export default LandingPage;
