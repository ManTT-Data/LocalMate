import { MantineProvider } from "@mantine/core";
import { ModalsProvider } from "@mantine/modals";
import appRoutes from "./routes/routes";
import { useRoutes } from "react-router-dom";
import { useEffect } from "react";
import { getCurrentUser } from "./apis/authService";
import useAuthStore from "./stores/useAuthStore";

import "./App.css";

function App() {
  const setUser = useAuthStore((state) => state.setUser);

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
      <ModalsProvider>{useRoutes(appRoutes)}</ModalsProvider>
    </MantineProvider>
  );
}

export default App;
