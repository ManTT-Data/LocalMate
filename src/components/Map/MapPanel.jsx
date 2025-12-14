import React, { useState } from "react";
import { Box, Stack } from "@mantine/core";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import ContextualToolbar from "../ContextualToolbar/ContextualToolbar";
import TripBadge from "../TripBadge/TripBadge";
import DestinationCard from "../DestinationCard/DestinationCard";
import GrabBookingWidget from "../BookingWidget/GrabBookingWidget";
import { userProfile, destinations } from "../../data/mockData";

// Fix for default marker icons in Leaflet with Webpack
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

// Custom marker icons
const userIcon = new L.DivIcon({
  className: "custom-marker",
  html: `
    <div class="flex flex-col items-center gap-1">
      <div class="size-4 rounded-full bg-blue-500 border-2 border-white shadow-lg animate-pulse"></div>
      <div class="bg-white px-2 py-1 rounded-md text-xs font-bold shadow-md whitespace-nowrap">You</div>
    </div>
  `,
  iconSize: [60, 60],
  iconAnchor: [30, 60],
});

const destinationIcon = new L.DivIcon({
  className: "custom-marker",
  html: `
    <div class="flex flex-col items-center gap-2">
      <div class="relative">
        <div class="absolute -bottom-1 left-1/2 -translate-x-1/2 w-0 h-0 border-l-[6px] border-l-transparent border-r-[6px] border-r-transparent border-t-[8px] border-t-[#13b6ec]"></div>
        <div class="bg-black text-white p-2 rounded-lg shadow-lg flex items-center gap-2 hover:scale-110 transition-transform">
          <span class="material-symbols-outlined text-[18px]">temple_buddhist</span>
          <span class="font-bold text-sm whitespace-nowrap">Marble Mountains</span>
        </div>
      </div>
    </div>
  `,
  iconSize: [200, 80],
  iconAnchor: [100, 80],
});

const MapPanel = () => {
  const [activeTab, setActiveTab] = useState(1);
  const center = [16.0282, 108.1322]; // Da Nang center

  return (
    <Box
      flex={1}
      style={{
        display: "flex",
        flexDirection: "column",
        backgroundColor: "var(--mantine-color-gray-1)",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Contextual Toolbar */}
      <Box
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          zIndex: 1000,
          padding: "1rem",
          pointerEvents: "none",
        }}
      >
        <Box
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
          }}
        >
          <ContextualToolbar activeTab={activeTab} onTabChange={setActiveTab} />
          <TripBadge />
        </Box>
      </Box>

      {/* Map Container */}
      <Box w="100%" h="100%" style={{ position: "relative" }}>
        <MapContainer
          center={center}
          zoom={12}
          className="w-full h-full"
          zoomControl={true}
          scrollWheelZoom={true}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* User Location Marker */}
          <Marker
            position={[userProfile.location.lat, userProfile.location.lng]}
            icon={userIcon}
          >
            <Popup>Your current location</Popup>
          </Marker>

          {/* Destination Markers */}
          {destinations.map((destination) => (
            <Marker
              key={destination.id}
              position={[destination.location.lat, destination.location.lng]}
              icon={destinationIcon}
            >
              <Popup>
                <div className="p-2">
                  <h3 className="font-bold">{destination.name}</h3>
                  <p className="text-sm text-slate-600">
                    {destination.description}
                  </p>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>

        {/* Floating Cards */}
        <Box
          style={{
            position: "absolute",
            bottom: "1.5rem",
            right: "1.5rem",
            left: "1.5rem",
            zIndex: 999,
            pointerEvents: "none",
          }}
          w={{ base: "auto", md: 380 }}
          ml={{ base: 0, md: "auto" }}
        >
          <Stack gap="md">
            <DestinationCard />
            <GrabBookingWidget />
          </Stack>
        </Box>
      </Box>
    </Box>
  );
};

export default MapPanel;
