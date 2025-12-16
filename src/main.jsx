import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import "./index.css";
import "leaflet/dist/leaflet.css";
// Mantine styles
import "@mantine/core/styles.css";
import "@mantine/dates/styles.css";
import "@mantine/dropzone/styles.css";
import "@mantine/notifications/styles.css";
import App from "./App.jsx";
import { PlanProvider } from "./contexts/PlanContext";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter>
      <PlanProvider>
        <App />
      </PlanProvider>
    </BrowserRouter>
  </StrictMode>
);
