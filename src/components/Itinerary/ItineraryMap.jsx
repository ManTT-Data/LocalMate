import React, { useEffect, useState, useMemo } from "react";
import PropTypes from "prop-types";
import {
  MapContainer,
  TileLayer,
  Marker,
  Polyline,
  useMap,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { getRoute, getTileLayerUrl } from "../../apis/graphhopper";
import useItineraryStore from "../../stores/useItineraryStore";
import useRouteCalculation from "../../hooks/useRouteCalculation";
import useGeolocation from "../../hooks/useGeolocation";
import { ActionIcon, Loader } from "@mantine/core";
import { IconCurrentLocation } from "@tabler/icons-react";
import {
  createCustomIcon,
  extractRoutePositions,
  extractWaypoints,
} from "./mapUtils";
import { MAP_DEFAULTS } from "./constants";
import RouteDebugger from "./RouteDebugger";

// Fix for default marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

// Custom user location icon
const userIcon = new L.DivIcon({
  className: "custom-marker",
  html: `
    <div class="flex flex-col items-center gap-1" style="transform: translate(-50%, -8px);">
      <div class="size-4 rounded-full bg-blue-500 border-2 border-white shadow-lg animate-pulse"></div>
      <div class="bg-white px-2 py-1 rounded-md text-xs font-bold shadow-md whitespace-nowrap">You</div>
    </div>
  `,
  iconSize: null,
  iconAnchor: [0, 0],
});

/**
 * Component to fit map bounds to route
 */
const FitBounds = ({ routeData }) => {
  const map = useMap();
  useEffect(() => {
    if (routeData && routeData.bbox) {
      const [minLon, minLat, maxLon, maxLat] = routeData.bbox;
      map.fitBounds(
        [
          [minLat, minLon],
          [maxLat, maxLon],
        ],
        { padding: MAP_DEFAULTS.FIT_BOUNDS_PADDING }
      );
    }
  }, [routeData, map]);
  return null;
};

FitBounds.propTypes = {
  routeData: PropTypes.object,
};

const ItineraryMap = ({
  dayIndex = 0, // Which day to display
  center = MAP_DEFAULTS.CENTER,
  zoom = MAP_DEFAULTS.ZOOM,
  routeColor = MAP_DEFAULTS.ROUTE_COLOR,
  routeWeight = MAP_DEFAULTS.ROUTE_WEIGHT,
  routeOpacity = MAP_DEFAULTS.ROUTE_OPACITY,
}) => {
  const [routeData, setRouteData] = useState(null);
  const [mapInstance, setMapInstance] = useState(null);

  // Get geolocation
  const { location: userLocation, error: locationError } = useGeolocation();

  // Get stops from Zustand store
  const { itineraryItems, includeUserLocation } = useItineraryStore();
  const stops = itineraryItems[dayIndex]?.stops || [];

  // Augment stops with user location if enabled
  const stopsForRouting = React.useMemo(() => {
    if (
      includeUserLocation &&
      userLocation.loaded &&
      userLocation.coordinates.lat
    ) {
      const userLocationStop = {
        id: "user-location-start",
        type: "start",
        name: "Your Location",
        snapshot: {
          lat: userLocation.coordinates.lat,
          lng: userLocation.coordinates.lng,
        },
      };
      return [userLocationStop, ...stops];
    }
    return stops;
  }, [includeUserLocation, userLocation, stops]);

  // Use route calculation hook (auto-recalculates when stops change)
  const { routeData: cachedRouteData } = useRouteCalculation(dayIndex);

  useEffect(() => {
    // Use cached route data if available
    if (cachedRouteData) {
      setRouteData(cachedRouteData);
      return;
    }

    // Otherwise fetch route manually
    const fetchRoute = async () => {
      const waypoints = extractWaypoints(stopsForRouting);

      if (waypoints.length > 1) {
        const data = await getRoute(waypoints);
        if (data) {
          setRouteData(data);
        }
      }
    };

    fetchRoute();
  }, [stopsForRouting, cachedRouteData]);

  // Memoize route positions extraction
  const routePositions = useMemo(
    () => extractRoutePositions(routeData),
    [routeData]
  );

  // Handle Locate Me button
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
    <div className="w-full h-full relative">
      <RouteDebugger
        routeData={routeData}
        routePositions={routePositions}
        stops={stops}
      />
      <MapContainer
        center={center}
        zoom={zoom}
        className="w-full h-full z-0"
        ref={setMapInstance}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url={getTileLayerUrl("standard")}
        />

        {routePositions.length > 0 && (
          <>
            {/* Glow Polyline */}
            <Polyline
              positions={routePositions}
              pathOptions={{
                color: routeColor,
                weight: routeWeight + 4,
                opacity: 0.2,
                lineJoin: "round",
                lineCap: "round",
              }}
            />
            {/* Animated Main Polyline */}
            <Polyline
              positions={routePositions}
              pathOptions={{
                className: "route-line-animated",
                color: routeColor,
                weight: routeWeight,
                opacity: routeOpacity,
                lineJoin: "round",
                lineCap: "round",
              }}
            />
          </>
        )}

        {stopsForRouting.map((stop, index) => {
          // Try to get position from multiple sources (in priority order)
          let position = null;

          // 1. From snapshot (newly added stops with snapshot)
          if (stop.snapshot?.lat && stop.snapshot?.lng) {
            position = { lat: stop.snapshot.lat, lng: stop.snapshot.lng };
          }
          // 2. From destination object directly (has lat/lng fields)
          else if (stop.destination?.lat && stop.destination?.lng) {
            position = { lat: stop.destination.lat, lng: stop.destination.lng };
          }
          // 3. From location or destination.location (legacy format)
          else {
            position = stop.location || stop.destination?.location;
          }

          if (!position || !position.lat || !position.lng) {
            console.warn(`Stop ${index} missing coordinates:`, stop);
            return null;
          }

          return (
            <Marker
              key={index}
              position={[position.lat, position.lng]}
              icon={createCustomIcon(stop)}
            ></Marker>
          );
        })}

        {/* User Location Marker */}
        {userLocation.loaded && userLocation.coordinates.lat && (
          <Marker
            position={[
              userLocation.coordinates.lat,
              userLocation.coordinates.lng,
            ]}
            icon={userIcon}
          />
        )}

        <FitBounds routeData={routeData} />
      </MapContainer>

      {/* Locate Me Button */}
      <ActionIcon
        variant="filled"
        color="white"
        size="xl"
        radius="xl"
        style={{
          position: "absolute",
          bottom: "1.5rem",
          right: "1.5rem",
          zIndex: 1000,
          boxShadow: "var(--mantine-shadow-md)",
          color: "var(--mantine-color-dark-4)",
        }}
        onClick={handleLocateMe}
        loading={!userLocation.loaded}
      >
        <IconCurrentLocation size={24} />
      </ActionIcon>

      {/* Helper Badge */}
      <div className="absolute top-[300px] left-[280px] pointer-events-none">
        {/* Can replicate the "floating" UI elements from HTML here if needed, but they are now map markers */}
      </div>
    </div>
  );
};

ItineraryMap.propTypes = {
  stops: PropTypes.arrayOf(
    PropTypes.shape({
      type: PropTypes.string,
      location: PropTypes.shape({
        lat: PropTypes.number.isRequired,
        lng: PropTypes.number.isRequired,
      }),
      destination: PropTypes.shape({
        name: PropTypes.string,
        image: PropTypes.string,
        location: PropTypes.shape({
          lat: PropTypes.number.isRequired,
          lng: PropTypes.number.isRequired,
        }),
      }),
      locationName: PropTypes.string,
      isTopPick: PropTypes.bool,
    })
  ).isRequired,
  center: PropTypes.arrayOf(PropTypes.number),
  zoom: PropTypes.number,
  routeColor: PropTypes.string,
  routeWeight: PropTypes.number,
  routeOpacity: PropTypes.number,
};

export default ItineraryMap;
