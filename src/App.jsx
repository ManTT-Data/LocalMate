import { MantineProvider } from "@mantine/core";
import { ModalsProvider } from "@mantine/modals";
import appRoutes from "./routes/routes";
import { useRoutes } from "react-router-dom";
import { useEffect } from "react";
import { getCurrentUser } from "./apis/authService";
import useUserStore from "./stores/useUserStore";

import "./App.css";

function App() {
  const setUser = useUserStore((state) => state.setUser);

  // Restore user session from localStorage on app mount
  useEffect(() => {
    const currentUser = getCurrentUser();
    if (currentUser) {
      setUser({
        id: currentUser.userId,
        email: currentUser.email,
        name: currentUser.fullName,
        avatar: currentUser.avatarUrl,
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
