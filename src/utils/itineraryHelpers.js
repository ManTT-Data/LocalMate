/**
 * Helper utilities for transforming itinerary data between frontend and backend formats
 */

/**
 * Transform backend itinerary to frontend format
 * @param {Object} backendItinerary - Itinerary from backend
 * @returns {Array} Frontend itinerary format (grouped by days)
 */
export const transformBackendToFrontend = (backendItinerary) => {
  if (!backendItinerary || !backendItinerary.stops) {
    return [];
  }

  const { stops, start_date, title } = backendItinerary;

  // Group stops by day_index
  const dayGroups = stops.reduce((acc, stop) => {
    // Backend uses 1-indexed, convert to 0-indexed for frontend
    const dayIndex = stop.day_index - 1;
    if (!acc[dayIndex]) {
      acc[dayIndex] = [];
    }
    acc[dayIndex].push(stop);
    return acc;
  }, {});

  // Transform to frontend format
  return Object.entries(dayGroups).map(([dayIndex, dayStops]) => {
    const dayNum = parseInt(dayIndex) + 1; // Display as Day 1, Day 2, etc.
    const date = calculateDate(start_date, dayNum);

    return {
      day: dayNum,
      title: `Day ${dayNum}`, // Can be customized per day if needed
      date: formatDate(date),
      totalCost: calculateTotalCost(dayStops),
      totalTime: calculateTotalTime(dayStops),
      stops: dayStops.map(transformStopToFrontend),
    };
  });
};

/**
 * Transform backend stop to frontend format
 * @param {Object} backendStop - Stop from backend
 * @returns {Object} Frontend stop format
 */
export const transformStopToFrontend = (backendStop) => {
  const { id, place_id, arrival_time, stay_minutes, notes, tags, snapshot } =
    backendStop;

  return {
    id,
    time: arrival_time || "08:00 AM",
    type: "destination", // Default type
    destinationId: place_id,
    destination: snapshot || {
      id: place_id,
      name: "Unknown Place",
    },
    isBooked: false, // Will be set from booking service
    notes,
    tags,
    stayMinutes: stay_minutes,
  };
};

/**
 * Transform frontend stop to backend format
 * @param {Object} frontendStop - Stop from frontend
 * @param {number} dayIndex - Day index (0-based from frontend)
 * @param {number} orderIndex - Order within day (0-based from frontend)
 * @param {string} itineraryId - Itinerary ID
 * @returns {Object} Backend stop create format
 */
export const transformStopToBackend = (
  frontendStop,
  dayIndex,
  orderIndex,
  itineraryId
) => {
  // Convert time string (e.g., "09:00") to datetime
  // Use today's date if not specified
  let arrivalTime = null;
  if (frontendStop.time) {
    const today = new Date();
    const [hours, minutes] = frontendStop.time.split(":");
    today.setHours(parseInt(hours), parseInt(minutes), 0, 0);
    arrivalTime = today.toISOString();
  }

  // Build snapshot from destination data
  let snapshot = null;
  if (frontendStop.destination) {
    snapshot = {
      name: frontendStop.destination.name,
      category: frontendStop.destination.category,
      address: frontendStop.destination.address,
      rating: frontendStop.destination.rating,
    };
  }

  return {
    // Backend expects 1-indexed (>= 1), frontend uses 0-indexed
    day_index: dayIndex + 1,
    order_index: orderIndex + 1,
    place_id:
      frontendStop.destinationId ||
      frontendStop.destination?.id ||
      frontendStop.destination?.place_id,
    arrival_time: arrivalTime,
    stay_minutes: frontendStop.stayMinutes || 60,
    notes: frontendStop.notes || null,
    tags: frontendStop.tags || [],
    snapshot: snapshot, // Include place data for backend
  };
};

/**
 * Calculate date from start_date and day offset
 * @param {string} startDate - ISO date string
 * @param {number} dayOffset - Day offset (1-based)
 * @returns {Date} Calculated date
 */
export const calculateDate = (startDate, dayOffset) => {
  const date = new Date(startDate);
  date.setDate(date.getDate() + (dayOffset - 1));
  return date;
};

/**
 * Format date for frontend display
 * @param {Date} date - Date object
 * @returns {string} Formatted date (e.g., "Oct 24")
 */
export const formatDate = (date) => {
  const months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ];
  return `${months[date.getMonth()]} ${date.getDate()}`;
};

/**
 * Calculate total cost for a day's stops
 * @param {Array} stops - Array of stops
 * @returns {string} Formatted cost (e.g., "1.2m VND")
 */
export const calculateTotalCost = (stops) => {
  // This would need to be calculated from booking data
  // For now, return placeholder
  return "0 VND";
};

/**
 * Calculate total time for a day's stops
 * @param {Array} stops - Array of stops
 * @returns {string} Formatted time (e.g., "4 hrs")
 */
export const calculateTotalTime = (stops) => {
  const totalMinutes = stops.reduce(
    (sum, stop) => sum + (stop.stay_minutes || 60),
    0
  );
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;

  if (hours > 0 && minutes > 0) {
    return `${hours} hrs ${minutes} mins`;
  } else if (hours > 0) {
    return `${hours} hrs`;
  } else {
    return `${minutes} mins`;
  }
};

/**
 * Create itinerary request for backend
 * @param {Object} params - Itinerary parameters
 * @returns {Object} Backend create request
 */
export const createItineraryRequest = ({
  title,
  startDate,
  endDate,
  totalDays,
  totalBudget,
  currency = "VND",
}) => {
  return {
    title,
    start_date: startDate,
    end_date: endDate,
    total_days: totalDays,
    total_budget: totalBudget,
    currency,
  };
};

/**
 * Calculate total days between dates
 * @param {string} startDate - Start date ISO string
 * @param {string} endDate - End date ISO string
 * @returns {number} Total days
 */
export const calculateTotalDays = (startDate, endDate) => {
  const start = new Date(startDate);
  const end = new Date(endDate);
  const diffTime = Math.abs(end - start);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays + 1; // Include both start and end day
};
