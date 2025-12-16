import { useEffect, useRef } from "react";
import { getRoute } from "../apis/graphhopper";
import useItineraryStore from "../stores/useItineraryStore";

/**
 * Custom hook for automatic route recalculation
 * Triggers when stops change for a specific day
 * @param {number} dayIndex - Index of the day to calculate route for
 * @returns {Object} Route calculation state
 */
const useRouteCalculation = (dayIndex) => {
  const { itineraryItems, updateRouteData, getRouteData } = useItineraryStore();
  const timeoutRef = useRef(null);

  useEffect(() => {
    // Clear any pending calculations
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    const day = itineraryItems[dayIndex];
    if (!day || !day.stops || day.stops.length < 2) {
      return;
    }

    // Debounce route calculation by 500ms
    timeoutRef.current = setTimeout(async () => {
      try {
        // Extract waypoints (locations) from stops
        const waypoints = day.stops
          .filter((stop) => stop.location || stop.destination?.location)
          .map((stop) => stop.location || stop.destination.location);

        if (waypoints.length < 2) {
          return;
        }

        // Call GraphHopper API
        const routeData = await getRoute(waypoints);

        if (routeData) {
          // Store in Zustand for caching
          updateRouteData(dayIndex, routeData);
        }
      } catch (error) {
        console.error("Route calculation error:", error);
      }
    }, 500);

    // Cleanup on unmount or dependency change
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [itineraryItems, dayIndex, updateRouteData]);

  return {
    routeData: getRouteData(dayIndex),
  };
};

export default useRouteCalculation;
