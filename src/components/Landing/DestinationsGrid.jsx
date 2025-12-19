import React from "react";
import {
  Container,
  Title,
  Text,
  Card,
  Image,
  Overlay,
  Anchor,
} from "@mantine/core";
import { IconStar } from "@tabler/icons-react";

const DestinationsGrid = () => {
  const destinations = [
    {
      id: 1,
      name: "Ba Na Hills",
      image:
        "https://lh3.googleusercontent.com/aida-public/AB6AXuCINw3vjqMSulPkHf2lWvsGM4D7cp5RvjstkGuFvBPzJE0hBV-wzKzfrvIyuyBkfpKRhbWxn_RIkjihLCcAiaqy9WkRwe8J_W9wiSiaA38dMynr6SRR1-gHarfMkJ7gycmpENaVqMSJ9RyQTN0e6Z9znrn1kGjux6vcYuPW0Ga2dNwdl2RjN2bT7nWlhzzK4C_D14lgAiekm1LKMDtsbM4Ln_zvJskmmo0J0fuyGK9Lr_pFHgyipHiq-5W97S_wyzXNZGgShOX1fXlg",
      rating: 4.9,
      reviews: "12k reviews",
    },
    {
      id: 2,
      name: "Marble Mountains",
      image:
        "https://lh3.googleusercontent.com/aida-public/AB6AXuDUUbYNPRb93C2PpOgACOTC4M4h7dJgwrXBN4gZT64FEhuaEMU7_LQ98qjZ2PcqxxNpENP0SOWsNZG5qbwFCQP_I9cwXaSCEpATWXUMPz5b5GwOIJxiqz7XAwxB2KSSe7ZxFy_yltNJqIeQGPtqw4CfMwAqtoooKESJg8TkKoKRF8o8cGW678rK44MsL7oVy4TNzUDxMnLGdGN0oTGMrPv2EXvKQLSpe9w3OsGFB1YJnXTELG3sYLgqvzrbmIgM3SulGLhmrl7hkS0r",
      rating: 4.7,
      reviews: "8k reviews",
    },
    {
      id: 3,
      name: "Hoi An Town",
      image:
        "https://lh3.googleusercontent.com/aida-public/AB6AXuClqR633fofHjfYnbyUJEU3PKBT-cvoL__r7l8ciI3BVCF5TNvlmfZWg1N00YWp4ocTKy_SpsJhZJ-mLISkChST15LAL0qLKHFIxzzcjFsf37LGnWT2BEImuKIXVFkgU_oxBFOstgtmR1Jib-e5-JgvNmchRd4BJrFu00S8wtiLj-wSKJ0ZhPXENBhq7t0zw2NJj1YeseBBPkE8ib-A-kt21L6S9iEfVwCW0YE3Zh9kWMAjOIoPEIhQcEaUpaerpT7C9q-vXFOrYN8w",
      rating: 4.9,
      reviews: "25k reviews",
    },
    {
      id: 4,
      name: "Son Tra Peninsula",
      image:
        "https://lh3.googleusercontent.com/aida-public/AB6AXuAd_5znrana39LYmJlcbj1RxOmlaRwWTVX8KYR3jcG1Pz_muEJqStOMfYvb0kjW47q5TEo0KUhUs5tZd88jT4mejFJkM7rJ3oyoJBGBrML5SWcpPLxIyvUSCyBVSulNEISywxEDjq5PJ34FmZw1BpkLAAhFYTYXf5PAsfHdq9LwBi77MJOF8vBbvfAIQLEAUhd6j3QR0haNXxWVtxEh-D8KrMZt9e2J-_L9FI7nB6vHhkyjleEKJQdozx9CyDkQjDSsjSDEnE54cbzx",
      rating: 4.8,
      reviews: "5k reviews",
    },
  ];

  return (
    <div id="destinations" className="py-20 bg-white">
      <Container size="xl">
        <div className="flex justify-between items-end mb-8 flex-wrap gap-4">
          <div>
            <Title order={2} className="text-3xl font-bold mb-2">
              Popular in Da Nang
            </Title>
            <Text c="dimmed" size="sm">
              Curated by AI based on thousands of traveler reviews.
            </Text>
          </div>
          <Anchor
            href="#"
            c="teal"
            fw={500}
            className="hidden sm:flex items-center hover:text-teal-700 transition-colors text-sm "
          >
            <span className="inline-flex items-center gap-1">
              View all destinations
              <span className="material-symbols-outlined ml-1 text-base">
                arrow_right_alt
              </span>
            </span>
          </Anchor>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {destinations.map((dest) => (
            <div
              key={dest.id}
              className="group relative overflow-hidden cursor-pointer rounded-3xl h-60 transition-transform hover:scale-[1.02]"
              style={{
                boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
              }}
            >
              <img
                src={dest.image}
                alt={dest.name}
                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
              />

              <div
                className="absolute inset-0"
                style={{
                  background:
                    "linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.3) 60%, rgba(0,0,0,0.8) 100%)",
                }}
              />

              <div className="absolute bottom-0 left-0 p-5 w-full z-10">
                <Title order={4} c="white" className="text-lg font-bold mb-1">
                  {dest.name}
                </Title>
                <div className="flex items-center gap-1.5">
                  <IconStar size={14} fill="#facc15" color="#facc15" />
                  <Text size="xs" c="white" fw={500}>
                    {dest.rating} ({dest.reviews})
                  </Text>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Container>
    </div>
  );
};

export default DestinationsGrid;
