import { MantineProvider } from "@mantine/core";
import { ModalsProvider } from "@mantine/modals";
import appRoutes from "./routes/routes";
import { useRoutes } from "react-router-dom";

import "./App.css";

function App() {
  return (
    <MantineProvider>
      <ModalsProvider>{useRoutes(appRoutes)}</ModalsProvider>
    </MantineProvider>
  );
}

export default App;
