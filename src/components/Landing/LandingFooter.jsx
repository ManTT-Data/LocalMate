import React from "react";
import {
  Container,
  Grid,
  Text,
  Anchor,
  Group,
  Box,
  Stack,
} from "@mantine/core";

const LandingFooter = () => {
  const footerSections = [
    {
      title: "Product",
      links: [
        { label: "For Tourists", href: "#" },
        { label: "For Drivers", href: "#" },
        { label: "Destinations", href: "#" },
        { label: "Pricing", href: "#" },
      ],
    },
    {
      title: "Company",
      links: [
        { label: "About Us", href: "#" },
        { label: "Careers", href: "#" },
        { label: "Blog", href: "#" },
        { label: "Contact", href: "#" },
      ],
    },
    {
      title: "Legal",
      links: [
        { label: "Privacy Policy", href: "#" },
        { label: "Terms of Service", href: "#" },
        { label: "Cookie Policy", href: "#" },
      ],
    },
  ];

  return (
    <Box
      component="footer"
      className="bg-white border-t border-gray-100 pt-16 pb-8"
    >
      <Container size="xl">
        <Grid gutter="xl" className="mb-12">
          <Grid.Col span={{ base: 12, md: 4 }}>
            <Group gap="sm" className="mb-4">
              <Box className="w-8 h-8 rounded-lg bg-gradient-to-br from-teal-500 to-blue-500 flex items-center justify-center text-white font-bold text-lg">
                L
              </Box>
              <Text fw={700} size="xl" className="tracking-tight">
                Localmate<span className="text-teal-500">.vn</span>
              </Text>
            </Group>

            <Text size="sm" c="dimmed" className="mb-4">
              Revolutionizing travel in Central Vietnam with cutting-edge AI
              technology.
            </Text>

            <Group gap="md">
              <Anchor
                href="#"
                c="dimmed"
                className="hover:text-teal-600 transition-colors"
              >
                <span className="sr-only">Facebook</span>
                <svg
                  className="h-6 w-6"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    fillRule="evenodd"
                    d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z"
                    clipRule="evenodd"
                  />
                </svg>
              </Anchor>

              <Anchor
                href="#"
                c="dimmed"
                className="hover:text-teal-600 transition-colors"
              >
                <span className="sr-only">Instagram</span>
                <svg
                  className="h-6 w-6"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    fillRule="evenodd"
                    d="M12.315 2c2.43 0 2.784.013 3.808.06 1.064.049 1.791.218 2.427.465a4.902 4.902 0 011.772 1.153 4.902 4.902 0 011.153 1.772c.247.636.416 1.363.465 2.427.048 1.067.06 1.407.06 4.123v.08c0 2.643-.012 2.987-.06 4.043-.049 1.064-.218 1.791-.465 2.427a4.902 4.902 0 01-1.153 1.772 4.902 4.902 0 01-1.772 1.153c-.636.247-1.363.416-2.427.465-1.067.048-1.407.06-4.123.06h-.08c-2.643 0-2.987-.012-4.043-.06-1.064-.049-1.791-.218-2.427-.465a4.902 4.902 0 01-1.772-1.153 4.902 4.902 0 01-1.153-1.772c-.247-.636-.416-1.363-.465-2.427-.047-1.024-.06-1.379-.06-3.808v-.63c0-2.43.013-2.784.06-3.808.049-1.064.218-1.791.465-2.427a4.902 4.902 0 011.153-1.772 4.902 4.902 0 011.772-1.153c.636-.247 1.363-.416 2.427-.465 1.067-.047 1.409-.06 3.809-.06h.63zm1.506 5.37c-1.713 0-3.097 1.385-3.097 3.097S12.108 13.564 13.821 13.564 16.918 12.18 16.918 10.467 15.534 7.37 13.821 7.37zm-3.097 8.192h.001c.005 0 .01 0 .015.001.005 0 .01 0 .015-.001h-.03zm5.127-9.563c-.44 0-.796.356-.796.796s.356.796.796.796.796-.356.796-.796-.356-.796-.796-.796z"
                    clipRule="evenodd"
                  />
                </svg>
              </Anchor>
            </Group>
          </Grid.Col>

          {footerSections.map((section, idx) => (
            <Grid.Col key={idx} span={{ base: 6, sm: 4, md: 2 }}>
              <Text fw={600} className="mb-4">
                {section.title}
              </Text>
              <Stack gap="sm">
                {section.links.map((link, linkIdx) => (
                  <Anchor
                    key={linkIdx}
                    href={link.href}
                    size="sm"
                    c="dimmed"
                    className="hover:text-teal-600 transition-colors"
                  >
                    {link.label}
                  </Anchor>
                ))}
              </Stack>
            </Grid.Col>
          ))}
        </Grid>

        <Box className="border-t border-gray-100 pt-8">
          <Group justify="space-between" className="flex-col md:flex-row">
            <Text size="sm" c="dimmed">
              © 2025 LocalMate. All rights reserved.
            </Text>

            <Group gap="lg">
              <Group gap="xs">
                <span className="w-2 h-2 rounded-full bg-green-500"></span>
                <Text size="sm" c="dimmed">
                  Systems Operational
                </Text>
              </Group>
            </Group>
          </Group>
        </Box>
      </Container>
    </Box>
  );
};

export default LandingFooter;
