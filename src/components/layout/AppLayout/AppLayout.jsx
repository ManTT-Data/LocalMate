import React from "react";
import { AppShell } from "@mantine/core";
import { Splitter } from "antd";
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
        <Splitter
          style={{ height: "100%", boxShadow: "0 0 10px rgba(0, 0, 0, 0.1)" }}
        >
          {/* Left Panel: Chat */}
          <Splitter.Panel
            defaultSize="30%"
            min="20%"
            max="50%"
            style={{ overflow: "hidden" }}
          >
            <ChatPanel onSendMessage={handleSendMessage} />
          </Splitter.Panel>

          {/* Right Panel: Content */}
          <Splitter.Panel style={{ overflow: "hidden" }}>
            {children}
          </Splitter.Panel>
        </Splitter>
      </AppShell.Main>
    </AppShell>
  );
};

export default AppLayout;
