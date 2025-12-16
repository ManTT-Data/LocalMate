import React, { useEffect } from "react";
import PropTypes from "prop-types";

/**
 * Temporary debugging component to log route data
 * Remove this after debugging
 */
const RouteDebugger = ({ routeData, routePositions, stops }) => {
  useEffect(() => {
    console.log("=== ROUTE DEBUG ===");
    console.log("Stops count:", stops?.length);
    console.log("Route data:", routeData);
    console.log("Route positions count:", routePositions?.length);
    if (routePositions?.length > 0) {
      console.log("First position:", routePositions[0]);
      console.log("Last position:", routePositions[routePositions.length - 1]);
    }
    console.log("==================");
  }, [routeData, routePositions, stops]);

  return null;
};

RouteDebugger.propTypes = {
  routeData: PropTypes.object,
  routePositions: PropTypes.array,
  stops: PropTypes.array,
};

export default RouteDebugger;
