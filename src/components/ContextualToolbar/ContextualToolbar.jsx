import React from "react";
import { Paper, Group, Button } from "@mantine/core";
import { contextualTabs } from "../../data/mockData";

const ContextualToolbar = ({ activeTab, onTabChange }) => {
  return (
    <Paper
      ml={32}
      p={4}
      radius="lg"
      shadow="sm"
      withBorder
      style={{
        backgroundColor: "rgba(255, 255, 255, 0.9)",
        backdropFilter: "blur(12px)",
        pointerEvents: "auto",
      }}
    >
      <Group gap={4}>
        {contextualTabs.map((tab) => (
          <Button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            variant={activeTab === tab.id ? "light" : "subtle"}
            color={activeTab === tab.id ? "black" : "gray"}
            size="sm"
            radius="md"
            leftSection={
              <span
                className="material-symbols-outlined"
                style={{ fontSize: "18px" }}
              >
                {tab.icon}
              </span>
            }
            styles={{
              root: {
                fontWeight: activeTab === tab.id ? 600 : 500,
                transition: "all 0.2s",
              },
            }}
          >
            {tab.label}
          </Button>
        ))}
      </Group>
    </Paper>
  );
};

export default ContextualToolbar;
