const GRAPHHOPPER_API_KEY = import.meta.env.VITE_GRAPHHOPPER_API_KEY;
const BASE_URL = "https://graphhopper.com/api/1";

/**
 * Calculates a route between two or more waypoints using GraphHopper.
 * @param {Array<{lat: number, lng: number}>} waypoints - Array of waypoints.
 * @param {string} vehicle - Vehicle type (car, foot, bike, motorcycle).
 * @param {object} options - Additional options (locale, instructions, etc).
 * @returns {Promise<Object>} - The route data in GeoJSON format (normalized).
 */
export const getRoute = async (waypoints, vehicle = "car", options = {}) => {
  if (!GRAPHHOPPER_API_KEY) {
    console.error(
      "GraphHopper API key is missing. Set VITE_GRAPHHOPPER_API_KEY in .env"
    );
    return null;
  }

  if (waypoints.length < 2) {
    console.warn("At least 2 waypoints required for routing");
    return null;
  }

  // Build query params
  const params = new URLSearchParams({
    key: GRAPHHOPPER_API_KEY,
    vehicle: vehicle,
    locale: options.locale || "en",
    instructions: options.instructions !== false,
    points_encoded: false, // Get raw coordinates
  });

  // Add waypoints as point parameters
  waypoints.forEach((wp) => {
    params.append("point", `${wp.lat},${wp.lng}`);
  });

  const url = `${BASE_URL}/route?${params.toString()}`;

  try {
    const response = await fetch(url);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(
        `GraphHopper API error: ${errorData.message || response.statusText}`
      );
    }

    const data = await response.json();

    // Normalize to GeoJSON format (similar to Geoapify)
    if (data.paths && data.paths.length > 0) {
      const path = data.paths[0];

      return {
        type: "FeatureCollection",
        features: [
          {
            type: "Feature",
            geometry: path.points, // Already GeoJSON LineString
            properties: {
              distance: path.distance, // in meters
              time: path.time / 1000, // convert ms to seconds
              ascend: path.ascend,
              descend: path.descend,
            },
          },
        ],
        bbox: path.bbox, // [minLon, minLat, maxLon, maxLat]
      };
    }

    return null;
  } catch (error) {
    console.error("Error fetching route from GraphHopper:", error);
    return null;
  }
};

/**
 * Optimizes a route using GraphHopper's Route Optimization API (TSP Solver).
 * This uses the /optimize endpoint which is part of the Route Optimization API.
 *
 * @param {Array<{lat: number, lng: number, id: string}>} locations - Array of locations to optimize.
 * @param {string} vehicle - Vehicle type (car, bike, foot).
 * @returns {Promise<Object>} - Optimized route with order and distances.
 */
export const optimizeRoute = async (locations, vehicle = "car") => {
  if (!GRAPHHOPPER_API_KEY) {
    console.error("GraphHopper API key is missing");
    return null;
  }

  if (locations.length < 2) {
    console.warn("At least 2 locations required for optimization");
    return null;
  }

  // Build optimization request
  const requestBody = {
    vehicles: [
      {
        vehicle_id: "vehicle-1",
        start_address: {
          location_id: locations[0].id || "start",
          lon: locations[0].lng,
          lat: locations[0].lat,
        },
        type_id: vehicle,
      },
    ],
    services: locations.slice(1).map((loc, index) => ({
      id: loc.id || `service-${index}`,
      name: loc.name || `Location ${index + 1}`,
      address: {
        location_id: loc.id || `loc-${index}`,
        lon: loc.lng,
        lat: loc.lat,
      },
    })),
    objectives: [
      {
        type: "min",
        value: "completion_time",
      },
    ],
  };

  const url = `${BASE_URL}/vrp/optimize?key=${GRAPHHOPPER_API_KEY}`;

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(
        `GraphHopper Optimization API error: ${
          errorData.message || response.statusText
        }`
      );
    }

    const data = await response.json();

    // Parse the optimized solution
    if (
      data.solution &&
      data.solution.routes &&
      data.solution.routes.length > 0
    ) {
      const route = data.solution.routes[0];

      return {
        optimized: true,
        order: route.activities.map((act) => act.location_id),
        distance: route.distance, // in meters
        duration: route.completion_time, // in seconds
        activities: route.activities,
      };
    }

    return null;
  } catch (error) {
    console.error("Error optimizing route with GraphHopper:", error);
    return null;
  }
};

/**
 * Simple TSP optimization using the Routing API with permutations.
 * This is a fallback if the Optimization API is not available.
 *
 * @param {Array<{lat: number, lng: number}>} waypoints - Array of waypoints.
 * @param {string} vehicle - Vehicle type.
 * @returns {Promise<Object>} - Best route order and distance.
 */
export const optimizeRouteSimple = async (waypoints, vehicle = "car") => {
  if (waypoints.length <= 2) {
    return {
      order: waypoints.map((_, i) => i),
      distance: 0,
    };
  }

  // For small sets (< 8 points), try permutations
  if (waypoints.length <= 7) {
    const results = [];

    // Generate some permutations (not all, to stay within API limits)
    const samples = Math.min(10, factorial(waypoints.length - 2));

    for (let i = 0; i < samples; i++) {
      const permuted = [
        waypoints[0],
        ...shuffle(waypoints.slice(1, -1)),
        waypoints[waypoints.length - 1],
      ];
      const route = await getRoute(permuted, vehicle);

      if (route && route.features[0]) {
        results.push({
          order: permuted.map((wp) => waypoints.indexOf(wp)),
          distance: route.features[0].properties.distance,
        });
      }
    }

    // Return the best one
    results.sort((a, b) => a.distance - b.distance);
    return results[0] || { order: waypoints.map((_, i) => i), distance: 0 };
  }

  // For larger sets, use nearest neighbor heuristic
  return nearestNeighborOptimization(waypoints);
};

// Helper: Shuffle array
function shuffle(array) {
  const arr = [...array];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

// Helper: Factorial
function factorial(n) {
  if (n <= 1) return 1;
  return n * factorial(n - 1);
}

// Helper: Haversine distance
function haversine(lat1, lng1, lat2, lng2) {
  const R = 6371000; // Earth's radius in meters
  const φ1 = (lat1 * Math.PI) / 180;
  const φ2 = (lat2 * Math.PI) / 180;
  const Δφ = ((lat2 - lat1) * Math.PI) / 180;
  const Δλ = ((lng2 - lng1) * Math.PI) / 180;

  const a =
    Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
    Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return R * c;
}

// Helper: Nearest Neighbor TSP
function nearestNeighborOptimization(waypoints) {
  const visited = new Array(waypoints.length).fill(false);
  const order = [0];
  visited[0] = true;
  let totalDistance = 0;

  for (let i = 0; i < waypoints.length - 1; i++) {
    const current = order[order.length - 1];
    let nearest = -1;
    let minDist = Infinity;

    for (let j = 0; j < waypoints.length; j++) {
      if (!visited[j]) {
        const dist = haversine(
          waypoints[current].lat,
          waypoints[current].lng,
          waypoints[j].lat,
          waypoints[j].lng
        );
        if (dist < minDist) {
          minDist = dist;
          nearest = j;
        }
      }
    }

    if (nearest !== -1) {
      order.push(nearest);
      visited[nearest] = true;
      totalDistance += minDist;
    }
  }

  return { order, distance: totalDistance };
}

/**
 * Get OpenStreetMap tile layer URL (GraphHopper doesn't provide tiles).
 * @param {string} style - Map style (standard, cycle, transport).
 * @returns {string} - Tile URL.
 */
export const getTileLayerUrl = (style = "standard") => {
  const styles = {
    standard: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    cycle: "https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png",
    transport: "https://{s}.tile.thunderforest.com/transport/{z}/{x}/{y}.png",
  };

  return styles[style] || styles.standard;
};
