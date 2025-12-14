import React, { useState } from "react";
import { Box, Stack, ActionIcon } from "@mantine/core";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { IconCurrentLocation } from "@tabler/icons-react";
import ContextualToolbar from "../ContextualToolbar/ContextualToolbar";
import TripBadge from "../TripBadge/TripBadge";
import DestinationCard from "../DestinationCard/DestinationCard";
import GrabBookingWidget from "../BookingWidget/GrabBookingWidget";
import { userProfile, destinations } from "../../data/mockData";
import useGeolocation from "../../hooks/useGeolocation";

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
    <div class="flex flex-col items-center gap-1" style="transform: translate(-50%, -8px);">
      <div class="size-4 rounded-full bg-blue-500 border-2 border-white shadow-lg animate-pulse"></div>
      <div class="bg-white px-2 py-1 rounded-md text-xs font-bold shadow-md whitespace-nowrap">You</div>
    </div>
  `,
  iconSize: null, // Let CSS control size
  iconAnchor: [0, 0], // Anchor at the map coordinates (which we align to center of dot via CSS)
});

const createDestinationIcon = (destination) => {
  return new L.DivIcon({
    className: "custom-marker",
    html: `
      <div class="flex flex-col items-center" style="transform: translate(-50%, -100%);">
        <div class="relative flex flex-col items-center">
          <div class="bg-black text-white p-2 rounded-lg shadow-lg flex items-center gap-2 hover:scale-110 transition-transform">
            <span class="material-symbols-outlined text-[18px]">temple_buddhist</span>
            <span class="font-bold text-sm whitespace-nowrap">${destination.name}</span>
          </div>
          <!-- Triangle pointer below the box -->
          <div class="w-0 h-0 border-l-[6px] border-l-transparent border-r-[6px] border-r-transparent border-t-[8px] border-t-black -mt-[1px]"></div>
        </div>
      </div>
    `,
    iconSize: null, // Dynamic size based on text
    iconAnchor: [0, 0], // Anchor at the map coordinates (bottom tip of triangle due to translate -100%)
  });
};

const MapPanel = () => {
  const [activeTab, setActiveTab] = useState(1);
  const [selectedDestination, setSelectedDestination] = useState(null);
  const center = [16.060793, 108.216996]; // Da Nang center
  const { location: userLocation, error: locationError } = useGeolocation();
  const [mapInstance, setMapInstance] = useState(null);

  const handleMarkerClick = (destination) => {
    setSelectedDestination(destination);
  };

  const handleCloseCards = () => {
    setSelectedDestination(null);
  };

  const handleLocateMe = () => {
    if (userLocation.loaded && userLocation.coordinates.lat && mapInstance) {
      mapInstance.flyTo(
        [userLocation.coordinates.lat, userLocation.coordinates.lng],
        14,
        {
          duration: 1.5,
        }
      );
    } else {
      console.warn("Location not ready or map not initialized");
    }
  };

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
          zoom={16}
          className="w-full h-full"
          zoomControl={true}
          scrollWheelZoom={true}
          ref={setMapInstance}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* User Location Marker */}
          {userLocation.loaded && !locationError ? (
            <Marker
              position={[
                userLocation.coordinates.lat,
                userLocation.coordinates.lng,
              ]}
              icon={userIcon}
            >
              <Popup>Your current location</Popup>
            </Marker>
          ) : (
            // Fallback to static user location if no geolocation
            <Marker
              position={[userProfile.location.lat, userProfile.location.lng]}
              icon={userIcon}
            >
              <Popup>Your profile location (Mock)</Popup>
            </Marker>
          )}

          {/* Destination Markers */}
          {destinations.map((destination) => (
            <Marker
              key={destination.id}
              position={[destination.location.lat, destination.location.lng]}
              icon={createDestinationIcon(destination)}
              eventHandlers={{
                click: () => handleMarkerClick(destination),
              }}
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

        {/* Locate Me Button */}
        <ActionIcon
          variant="filled"
          color="white"
          size="xl"
          radius="xl"
          style={{
            position: "absolute",
            bottom: selectedDestination ? "240px" : "1.5rem",
            right: "1.5rem",
            zIndex: 1000,
            boxShadow: "var(--mantine-shadow-md)",
            color: "var(--mantine-color-dark-4)",
            transition: "bottom 0.3s ease",
          }}
          onClick={handleLocateMe}
          loading={!userLocation.loaded}
        >
          <IconCurrentLocation size={24} />
        </ActionIcon>

        {/* Floating Cards */}
        {selectedDestination && (
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
              <DestinationCard
                destination={selectedDestination}
                onClose={handleCloseCards}
              />
              <GrabBookingWidget onClose={handleCloseCards} />
            </Stack>
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default MapPanel;
