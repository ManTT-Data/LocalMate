import React from "react";
import { AppShell, Flex } from "@mantine/core";
import Header from "../components/layout/Header/Header";
import ChatPanel from "../components/ChatPanel/ChatPanel";
import MapPanel from "../components/Map/MapPanel";

const DaNangTourism = () => {
  const handleSendMessage = (message) => {
    console.log("Sending message:", message);
    // TODO: Implement message sending logic
  };

  return (
    <AppShell
      header={{ height: 60 }}
      padding={0}
      styles={{
        main: {
          height: "100vh",
          overflow: "hidden",
          padding: 0,
        },
      }}
    >
      <AppShell.Header>
        <Header />
      </AppShell.Header>

      <AppShell.Main>
        <Flex h="100%" style={{ overflow: "hidden" }}>
          {/* Left Panel: Chat */}
          <ChatPanel onSendMessage={handleSendMessage} />

          {/* Right Panel: Map */}
          <MapPanel />
        </Flex>
      </AppShell.Main>
    </AppShell>
  );
};

export default DaNangTourism;
