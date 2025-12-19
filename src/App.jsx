import { MantineProvider } from "@mantine/core";
import { ModalsProvider } from "@mantine/modals";
import { useRoutes, useLocation } from "react-router-dom";
import React, { useEffect } from "react";
import { AnimatePresence } from "framer-motion";
import appRoutes from "./routes/routes";
import { getCurrentUser } from "./apis/authService";
import useAuthStore from "./stores/useAuthStore";

import "./App.css";

function App() {
  const setUser = useAuthStore((state) => state.setUser);

  const element = useRoutes(appRoutes);
  const location = useLocation();

  // Restore user session from localStorage on app mount
  useEffect(() => {
    const currentUser = getCurrentUser();
    if (currentUser) {
      setUser({
        userId: currentUser.userId,
        email: currentUser.email,
        fullName: currentUser.fullName,
        avatarUrl: currentUser.avatarUrl,
      });
    }
  }, [setUser]);

  return (
    <MantineProvider>
      <ModalsProvider>
        <AnimatePresence mode="wait">
          {element && React.cloneElement(element, { key: location.pathname })}
        </AnimatePresence>
      </ModalsProvider>
    </MantineProvider>
  );
}

export default App;
