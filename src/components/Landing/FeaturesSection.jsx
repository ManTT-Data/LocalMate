import React from "react";
import { Container, Title, Text, Anchor } from "@mantine/core";
import {
  IconMap,
  IconCar,
  IconCircleCheck,
  IconArrowRight,
} from "@tabler/icons-react";

const FeaturesSection = () => {
  const features = [
    {
      id: "tourists",
      icon: <IconMap size={28} />,
      iconBg: "bg-blue-50",
      iconColor: "text-blue-600",
      title: "AI Travel Planner",
      description:
        "Personalized itineraries generated in seconds. Discover hidden cafes, plan optimal routes, and get real-time cultural insights as you explore.",
      benefits: [
        "Multimodal Itinerary Creation",
        "Real-time Weather Adaptations",
        "Local Cuisine Recommendations",
      ],
      linkText: "Plan My Trip",
      linkHref: "#tourists",
      linkColor: "text-blue-600",
    },
    {
      id: "drivers",
      icon: <IconCar size={28} />,
      iconBg: "bg-green-50",
      iconColor: "text-green-600",
      title: "AI Guide Pack",
      description:
        "Empower your service with knowledge. Get instant answers about landmarks, history, and tips to share with your passengers, becoming a 5-star local guide.",
      benefits: [
        "Instant Landmark Facts",
        "Conversation Starters for Tourists",
        "Traffic & Route Optimization Tips",
      ],
      linkText: "Enhance My Service",
      linkHref: "#drivers",
      linkColor: "text-green-600",
    },
  ];

  return (
    <div id="features" className="py-20 bg-gray-50">
      <Container size="xl">
        <div className="flex flex-col md:flex-row gap-6">
          {features.map((feature) => (
            <div
              key={feature.id}
              className="bg-white rounded-2xl p-8 hover:shadow-lg transition-shadow duration-300"
            >
              <div
                className={`w-12 h-12 ${feature.iconBg} rounded-xl flex items-center justify-center mb-6 ${feature.iconColor}`}
              >
                {feature.icon}
              </div>

              <Title order={3} className="text-2xl font-bold mb-3">
                {feature.title}
              </Title>

              <Text size="sm" c="dimmed" className="mb-6 leading-relaxed">
                {feature.description}
              </Text>

              <div className="space-y-3 mb-6">
                {feature.benefits.map((benefit, idx) => (
                  <div key={idx} className="flex items-start gap-2">
                    <IconCircleCheck
                      size={18}
                      className="text-teal-500 mt-0.5 flex-shrink-0"
                    />
                    <Text size="sm" c="dimmed">
                      {benefit}
                    </Text>
                  </div>
                ))}
              </div>

              <Anchor
                href={feature.linkHref}
                fw={600}
                className={`${feature.linkColor} hover:underline transition-all`}
              >
                <span className="inline-flex items-center gap-1 mt-2 whitespace-nowrap">
                  {feature.linkText} <IconArrowRight size={16} stroke={2.5} />
                </span>
              </Anchor>
            </div>
          ))}
        </div>
      </Container>
    </div>
  );
};

export default FeaturesSection;
