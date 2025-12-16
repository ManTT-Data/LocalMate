/**
 * Mock Backend Service for User Management
 * Simulates API calls for user profile and preferences
 */

import { userProfile, userPreferences } from "../data/mockData";

/**
 * Simulate network delay
 * @param {number} min - Minimum delay in ms
 * @param {number} max - Maximum delay in ms
 */
const simulateDelay = (min = 500, max = 1500) => {
  const delay = Math.floor(Math.random() * (max - min + 1)) + min;
  return new Promise((resolve) => setTimeout(resolve, delay));
};

/**
 * Simulate occasional API failures (10% chance)
 */
const shouldFail = () => Math.random() < 0.1;

/**
 * Fetch user profile
 * @param {string} userId - User ID
 * @returns {Promise<Object>} User profile data
 */
export const fetchUserProfileAPI = async (userId) => {
  await simulateDelay();

  if (shouldFail()) {
    throw new Error("Failed to fetch user profile");
  }

  // Return mock user profile with userId added
  return {
    ...userProfile,
    userId: userId || "user-001",
    email: "traveler@example.com",
    phone: "+84 123 456 789",
    joinedDate: "2024-01-15",
    verified: true,
  };
};

/**
 * Update user profile
 * @param {string} userId - User ID
 * @param {Object} updates - Profile fields to update
 * @returns {Promise<Object>} Update result
 */
export const updateUserProfileAPI = async (userId, updates) => {
  await simulateDelay(500, 1000);

  if (shouldFail()) {
    throw new Error("Failed to update profile");
  }

  return {
    success: true,
    userId,
    updates,
    updatedAt: new Date().toISOString(),
    message: "Profile updated successfully",
  };
};

/**
 * Update user location
 * @param {string} userId - User ID
 * @param {Object} location - Location object with lat, lng
 * @returns {Promise<Object>} Update result
 */
export const updateUserLocationAPI = async (userId, location) => {
  await simulateDelay(300, 600);

  if (shouldFail()) {
    throw new Error("Failed to update location");
  }

  return {
    success: true,
    userId,
    location,
    updatedAt: new Date().toISOString(),
    message: "Location updated successfully",
  };
};

/**
 * Fetch user preferences
 * @param {string} userId - User ID
 * @returns {Promise<Object>} User preferences
 */
export const fetchUserPreferencesAPI = async (userId) => {
  await simulateDelay(400, 900);

  if (shouldFail()) {
    throw new Error("Failed to fetch user preferences");
  }

  // Return mock preferences with userId
  return {
    ...userPreferences,
    userId: userId || "user-001",
  };
};

/**
 * Update user preferences
 * @param {string} userId - User ID
 * @param {Object} preferences - Preference fields to update
 * @returns {Promise<Object>} Update result
 */
export const updateUserPreferencesAPI = async (userId, preferences) => {
  await simulateDelay(400, 800);

  if (shouldFail()) {
    throw new Error("Failed to update preferences");
  }

  return {
    success: true,
    userId,
    preferences,
    updatedAt: new Date().toISOString(),
    message: "Preferences updated successfully",
  };
};

/**
 * Update notification settings
 * @param {string} userId - User ID
 * @param {Object} notificationSettings - Notification settings
 * @returns {Promise<Object>} Update result
 */
export const updateNotificationSettingsAPI = async (
  userId,
  notificationSettings
) => {
  await simulateDelay(300, 600);

  if (shouldFail()) {
    throw new Error("Failed to update notification settings");
  }

  return {
    success: true,
    userId,
    notifications: notificationSettings,
    updatedAt: new Date().toISOString(),
    message: "Notification settings updated successfully",
  };
};

/**
 * Add saved location
 * @param {string} userId - User ID
 * @param {Object} location - Location object with name, lat, lng
 * @returns {Promise<Object>} Result
 */
export const addSavedLocationAPI = async (userId, location) => {
  await simulateDelay(400, 700);

  if (shouldFail()) {
    throw new Error("Failed to save location");
  }

  return {
    success: true,
    userId,
    location,
    savedAt: new Date().toISOString(),
    message: "Location saved successfully",
  };
};

/**
 * Remove saved location
 * @param {string} userId - User ID
 * @param {string} locationId - Location ID or index
 * @returns {Promise<Object>} Result
 */
export const removeSavedLocationAPI = async (userId, locationId) => {
  await simulateDelay(300, 600);

  if (shouldFail()) {
    throw new Error("Failed to remove location");
  }

  return {
    success: true,
    userId,
    locationId,
    removedAt: new Date().toISOString(),
    message: "Location removed successfully",
  };
};

/**
 * Add to recent searches
 * @param {string} userId - User ID
 * @param {string} searchTerm - Search term
 * @returns {Promise<Object>} Result
 */
export const addRecentSearchAPI = async (userId, searchTerm) => {
  await simulateDelay(200, 400);

  // Don't fail for this operation as it's not critical
  return {
    success: true,
    userId,
    searchTerm,
    addedAt: new Date().toISOString(),
  };
};

/**
 * Clear recent searches
 * @param {string} userId - User ID
 * @returns {Promise<Object>} Result
 */
export const clearRecentSearchesAPI = async (userId) => {
  await simulateDelay(200, 400);

  if (shouldFail()) {
    throw new Error("Failed to clear search history");
  }

  return {
    success: true,
    userId,
    clearedAt: new Date().toISOString(),
    message: "Search history cleared",
  };
};

/**
 * Upload user avatar
 * @param {string} userId - User ID
 * @param {File} avatarFile - Avatar image file
 * @returns {Promise<Object>} Upload result
 */
export const uploadAvatarAPI = async (userId, avatarFile) => {
  await simulateDelay(1000, 2500);

  if (shouldFail()) {
    throw new Error("Failed to upload avatar");
  }

  // Simulate successful upload and return a URL
  const avatarUrl = URL.createObjectURL(avatarFile);

  return {
    success: true,
    userId,
    avatarUrl,
    uploadedAt: new Date().toISOString(),
    message: "Avatar uploaded successfully",
  };
};

/**
 * Verify user account
 * @param {string} userId - User ID
 * @param {string} verificationCode - Verification code
 * @returns {Promise<Object>} Verification result
 */
export const verifyUserAccountAPI = async (userId, verificationCode) => {
  await simulateDelay(600, 1200);

  if (shouldFail()) {
    throw new Error("Verification failed. Please try again.");
  }

  return {
    success: true,
    userId,
    verified: true,
    verifiedAt: new Date().toISOString(),
    message: "Account verified successfully",
  };
};
