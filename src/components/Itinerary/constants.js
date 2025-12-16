/**
 * Itinerary Component Constants
 * Centralized configuration for colors, sizes, and other magic values
 */

// Z-Index layers
export const Z_INDEX = {
  TIMELINE_LINE: 0,
  TIMELINE_DOT: 10,
  TRAVEL_BADGE: 10,
  STICKY_HEADER: 10,
};

// Colors
export const COLORS = {
  TIMELINE_LINE: "gray.2",
  TOP_PICK: "orange",
  DESTINATION: "blue",
  PLAN_ITEM: "green",
  START_LOCATION: "gray",
  ROUTE_DEFAULT: "#3b82f6", // Blue-500
  HIGHLIGHT_BORDER: "#10b981", // Green-500
  BOOKED_BORDER: "#10b981", // Green-500
};

// Sizes
export const SIZES = {
  TIMELINE_DOT: 22,
  TIMELINE_DOT_BORDER: 2,
  TIMELINE_LINE_WIDTH: 2,
  TIMELINE_LINE_LEFT_OFFSET: 7,
  TIMELINE_DOT_LEFT_OFFSET: -3,
  TIMELINE_DOT_TOP_OFFSET: 6,
  CONTENT_PADDING_LEFT: 32,
  THUMBNAIL_SIZE: 56,
  DRAG_HANDLE_SIZE: 18,
};

// Animation
export const ANIMATIONS = {
  TRANSITION_DURATION: "0.2s",
  PULSE_DURATION: "2s",
};

// Map
export const MAP_DEFAULTS = {
  CENTER: [16.0544, 108.2022], // Da Nang
  ZOOM: 13,
  ROUTE_COLOR: "#2563eb", // Brighter blue (blue-600)
  ROUTE_WEIGHT: 6, // Thicker line
  ROUTE_OPACITY: 0.9, // More opaque
  FIT_BOUNDS_PADDING: [50, 50],
};

// Drag and Drop
export const DND_TYPES = {
  PLAN_ITEMS: "plan-items",
  STOPS: "stops",
};

// Component Variants
export const STOP_TYPES = {
  START: "start",
  DESTINATION: "destination",
};
