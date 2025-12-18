// Hardcoded test user for development/testing
export const HARDCODED_TEST_USER = {
  userId: "00000000-0000-0000-0000-000000000001", // Valid UUID format for test user
  email: "testuser@localmate.com",
  username: "testuser",
  fullName: "Test User",
  avatarUrl: "https://api.dicebear.com/7.x/avataaars/svg?seed=TestUser",
  sessionId: "test-session-default",
};

export const googlClientId =
  "261949591384-cvb3pf4lveqdkorql609mf95gia0pn0r.apps.googleusercontent.com";

export const baseUrl = "https://cuong2004-localmate.hf.space";
// export const baseUrl = "http://127.0.0.1:8000/";

export const API_VERSION = "/api/v1";

export const apiUrls = {
  // Authentication
  auth: {
    login: `${API_VERSION}/auth/login`,
    logout: `${API_VERSION}/auth/logout`,
  },

  // Upload API
  upload: {
    image: `${API_VERSION}/upload/image`,
  },

  // Chat API
  chat: {
    send: `${API_VERSION}/chat`,
    clear: `${API_VERSION}/chat/clear`,
    history: (userId) => `${API_VERSION}/chat/history/${userId}`,
    messages: (userId, sessionId = "default") =>
      `${API_VERSION}/chat/messages/${userId}?session_id=${sessionId}`,
  },

  // Image Search
  imageSearch: `${API_VERSION}/search/image`,

  // Trip Planner API
  planner: {
    create: `${API_VERSION}/planner/create`,
    getUserPlans: `${API_VERSION}/planner/user/plans`,
    get: (planId) => `${API_VERSION}/planner/${planId}`,
    delete: (planId) => `${API_VERSION}/planner/${planId}`,
    add: (planId) => `${API_VERSION}/planner/${planId}/add`,
    remove: (planId, itemId) =>
      `${API_VERSION}/planner/${planId}/remove/${itemId}`,
    reorder: (planId) => `${API_VERSION}/planner/${planId}/reorder`,
    optimize: (planId) => `${API_VERSION}/planner/${planId}/optimize`,
    replace: (planId, itemId) =>
      `${API_VERSION}/planner/${planId}/replace/${itemId}`,
  },

  // Itinerary Management API
  itinerary: {
    list: `${API_VERSION}/itineraries`,
    create: `${API_VERSION}/itineraries`,
    get: (id) => `${API_VERSION}/itineraries/${id}`,
    update: (id) => `${API_VERSION}/itineraries/${id}`,
    delete: (id) => `${API_VERSION}/itineraries/${id}`,
    addStop: (id) => `${API_VERSION}/itineraries/${id}/stops`,
    updateStop: (id, stopId) =>
      `${API_VERSION}/itineraries/${id}/stops/${stopId}`,
    deleteStop: (id, stopId) =>
      `${API_VERSION}/itineraries/${id}/stops/${stopId}`,
  },

  // User Profile API
  users: {
    me: `${API_VERSION}/users/me`,
    byId: (userId) => `${API_VERSION}/users/${userId}`,
  },

  // Utility Endpoints
  health: "/health",
  nearby: `${API_VERSION}/nearby`,
};
