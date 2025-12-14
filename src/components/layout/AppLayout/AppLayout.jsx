import React from "react";
import { AppShell, Flex } from "@mantine/core";
import Header from "../Header/Header";
import ChatPanel from "../../ChatPanel/ChatPanel";

const AppLayout = ({ children }) => {
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
        },
      }}
    >
      <AppShell.Header zIndex={1100}>
        <Header />
      </AppShell.Header>

      <AppShell.Main>
        <Flex h="100%" style={{ overflow: "hidden" }}>
          {/* Left Panel: Chat */}
          <ChatPanel onSendMessage={handleSendMessage} />

          {/* Right Panel: Content */}
          {children}
        </Flex>
      </AppShell.Main>
    </AppShell>
  );
};

export default AppLayout;
