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

  // Get stops from Zustand store
  const { itineraryItems } = useItineraryStore();
  const stops = itineraryItems[dayIndex]?.stops || [];

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
      const waypoints = extractWaypoints(stops);

      if (waypoints.length > 1) {
        const data = await getRoute(waypoints);
        if (data) {
          setRouteData(data);
        }
      }
    };

    fetchRoute();
  }, [stops, cachedRouteData]);

  // Memoize route positions extraction
  const routePositions = useMemo(
    () => extractRoutePositions(routeData),
    [routeData]
  );

  return (
    <div className="w-full h-full relative">
      <RouteDebugger
        routeData={routeData}
        routePositions={routePositions}
        stops={stops}
      />
      <MapContainer center={center} zoom={zoom} className="w-full h-full z-0">
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url={getTileLayerUrl("standard")}
        />

        {routePositions.length > 0 && (
          <Polyline
            positions={routePositions}
            pathOptions={{
              color: routeColor,
              weight: routeWeight,
              opacity: routeOpacity,
              lineJoin: "round",
              lineCap: "round",
            }}
          />
        )}

        {stops.map((stop, index) => {
          const position = stop.location || stop.destination?.location;
          if (!position) return null;

          return (
            <Marker
              key={index}
              position={[position.lat, position.lng]}
              icon={createCustomIcon(stop)}
            ></Marker>
          );
        })}

        <FitBounds routeData={routeData} />
      </MapContainer>

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
