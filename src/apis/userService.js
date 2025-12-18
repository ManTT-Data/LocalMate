/**
 * User Service - Real Backend API
 * Handles user profile and preferences management
 */

import axios from "axios";
import { baseUrl, apiUrls } from "../utils/constants";
import { getAuthToken } from "./authService";

/**
 * Create axios instance with auth interceptor
 */
const createAuthAxios = () => {
  const instance = axios.create({
    baseURL: baseUrl,
    headers: {
      "Content-Type": "application/json",
    },
  });

  // Add auth token to requests
  instance.interceptors.request.use(
    (config) => {
      const token = getAuthToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  return instance;
};

/**
 * Fetch current user profile
 * @param {string} userId - User ID
 * @returns {Promise<Object>} User profile data
 */
export const fetchUserProfileAPI = async (userId) => {
  try {
    const api = createAuthAxios();
    const response = await api.get(apiUrls.users.me, {
      params: { user_id: userId },
    });

    return response.data.profile;
  } catch (error) {
    console.error("Failed to fetch user profile:", error);
    throw new Error(
      error.response?.data?.detail || "Failed to fetch user profile"
    );
  }
};

/**
 * Fetch user profile by ID
 * @param {string} userId - User ID
 * @returns {Promise<Object>} User profile data
 */
export const fetchUserProfileByIdAPI = async (userId) => {
  try {
    const api = createAuthAxios();
    const response = await api.get(apiUrls.users.byId(userId));

    return response.data.profile;
  } catch (error) {
    console.error("Failed to fetch user profile by ID:", error);
    throw new Error(
      error.response?.data?.detail || "Failed to fetch user profile"
    );
  }
};

/**
 * Update user profile
 * @param {string} userId - User ID
 * @param {Object} updates - Profile fields to update
 * @param {string} [updates.full_name] - Full name
 * @param {string} [updates.phone] - Phone number
 * @param {string} [updates.locale] - Locale (e.g., 'vi_VN', 'en_US')
 * @param {string} [updates.avatar_url] - Avatar URL
 * @returns {Promise<Object>} Updated profile
 */
export const updateUserProfileAPI = async (userId, updates) => {
  try {
    const api = createAuthAxios();
    const response = await api.put(apiUrls.users.me, updates, {
      params: { user_id: userId },
    });

    return response.data.profile;
  } catch (error) {
    console.error("Failed to update profile:", error);
    throw new Error(error.response?.data?.detail || "Failed to update profile");
  }
};

/**
 * Update user avatar
 * @param {string} userId - User ID
 * @param {string} avatarUrl - New avatar URL
 * @returns {Promise<Object>} Updated profile
 */
export const updateUserAvatarAPI = async (userId, avatarUrl) => {
  try {
    const api = createAuthAxios();
    const response = await api.put(
      apiUrls.users.me,
      { avatar_url: avatarUrl },
      {
        params: { user_id: userId },
      }
    );

    return response.data.profile;
  } catch (error) {
    console.error("Failed to update avatar:", error);
    throw new Error(error.response?.data?.detail || "Failed to update avatar");
  }
};

/**
 * Upload user avatar (using file upload)
 * Note: This requires a file upload endpoint on the backend
 * For now, this is a placeholder that returns the URL
 * @param {string} userId - User ID
 * @param {File} avatarFile - Avatar image file
 * @returns {Promise<Object>} Upload result with avatar URL
 */
export const uploadAvatarAPI = async (userId, avatarFile) => {
  try {
    // TODO: Implement actual file upload to backend
    // For now, create a local URL (this should be replaced with actual upload)
    const avatarUrl = URL.createObjectURL(avatarFile);

    // Update profile with new avatar URL
    const profile = await updateUserAvatarAPI(userId, avatarUrl);

    return {
      success: true,
      userId,
      avatarUrl: profile.avatar_url,
      uploadedAt: new Date().toISOString(),
      message: "Avatar uploaded successfully",
    };
  } catch (error) {
    console.error("Failed to upload avatar:", error);
    throw new Error(error.response?.data?.detail || "Failed to upload avatar");
  }
};

/**
 * Update user locale/language preference
 * @param {string} userId - User ID
 * @param {string} locale - Locale code (e.g., 'vi_VN', 'en_US')
 * @returns {Promise<Object>} Updated profile
 */
export const updateUserLocaleAPI = async (userId, locale) => {
  try {
    const api = createAuthAxios();
    const response = await api.put(
      apiUrls.users.me,
      { locale },
      {
        params: { user_id: userId },
      }
    );

    return response.data.profile;
  } catch (error) {
    console.error("Failed to update locale:", error);
    throw new Error(error.response?.data?.detail || "Failed to update locale");
  }
};

/**
 * Update user phone number
 * @param {string} userId - User ID
 * @param {string} phone - Phone number
 * @returns {Promise<Object>} Updated profile
 */
export const updateUserPhoneAPI = async (userId, phone) => {
  try {
    const api = createAuthAxios();
    const response = await api.put(
      apiUrls.users.me,
      { phone },
      {
        params: { user_id: userId },
      }
    );

    return response.data.profile;
  } catch (error) {
    console.error("Failed to update phone:", error);
    throw new Error(
      error.response?.data?.detail || "Failed to update phone number"
    );
  }
};

// ========== Legacy Mock API Functions (Deprecated) ==========
// These functions are kept for backward compatibility
// They should be migrated to use backend APIs when available

/**
 * @deprecated Use backend preferences API when available
 * Update user location (currently stored in localStorage)
 */
export const updateUserLocationAPI = async (userId, location) => {
  try {
    // Store in localStorage for now
    const locationData = {
      userId,
      location,
      updatedAt: new Date().toISOString(),
    };
    localStorage.setItem("user_location", JSON.stringify(locationData));

    return {
      success: true,
      userId,
      location,
      updatedAt: locationData.updatedAt,
      message: "Location updated successfully",
    };
  } catch (error) {
    console.error("Failed to update location:", error);
    throw new Error("Failed to update location");
  }
};

/**
 * @deprecated Use backend preferences API when available
 * Fetch user preferences (currently from localStorage)
 */
export const fetchUserPreferencesAPI = async (userId) => {
  try {
    const prefsData = localStorage.getItem("user_preferences");
    if (prefsData) {
      return JSON.parse(prefsData);
    }

    // Return default preferences
    return {
      userId,
      preferredLanguage: "vi",
      travelStyle: "balanced",
      notifications: {
        email: true,
        push: true,
        sms: false,
      },
      savedLocations: [],
      recentSearches: [],
    };
  } catch (error) {
    console.error("Failed to fetch preferences:", error);
    throw new Error("Failed to fetch user preferences");
  }
};

/**
 * @deprecated Use backend preferences API when available
 * Update user preferences (currently in localStorage)
 */
export const updateUserPreferencesAPI = async (userId, preferences) => {
  try {
    const currentPrefs = await fetchUserPreferencesAPI(userId);
    const updatedPrefs = {
      ...currentPrefs,
      ...preferences,
      userId,
      updatedAt: new Date().toISOString(),
    };

    localStorage.setItem("user_preferences", JSON.stringify(updatedPrefs));

    return {
      success: true,
      userId,
      preferences: updatedPrefs,
      updatedAt: updatedPrefs.updatedAt,
      message: "Preferences updated successfully",
    };
  } catch (error) {
    console.error("Failed to update preferences:", error);
    throw new Error("Failed to update preferences");
  }
};

/**
 * @deprecated Use backend preferences API when available
 * Update notification settings
 */
export const updateNotificationSettingsAPI = async (
  userId,
  notificationSettings
) => {
  try {
    const currentPrefs = await fetchUserPreferencesAPI(userId);
    const updatedPrefs = {
      ...currentPrefs,
      notifications: {
        ...currentPrefs.notifications,
        ...notificationSettings,
      },
      updatedAt: new Date().toISOString(),
    };

    localStorage.setItem("user_preferences", JSON.stringify(updatedPrefs));

    return {
      success: true,
      userId,
      notifications: updatedPrefs.notifications,
      updatedAt: updatedPrefs.updatedAt,
      message: "Notification settings updated successfully",
    };
  } catch (error) {
    console.error("Failed to update notification settings:", error);
    throw new Error("Failed to update notification settings");
  }
};

/**
 * @deprecated Use backend preferences API when available
 * Add saved location
 */
export const addSavedLocationAPI = async (userId, location) => {
  try {
    const currentPrefs = await fetchUserPreferencesAPI(userId);
    const savedLocations = currentPrefs.savedLocations || [];

    savedLocations.push({
      ...location,
      id: Date.now().toString(),
      savedAt: new Date().toISOString(),
    });

    const updatedPrefs = {
      ...currentPrefs,
      savedLocations,
      updatedAt: new Date().toISOString(),
    };

    localStorage.setItem("user_preferences", JSON.stringify(updatedPrefs));

    return {
      success: true,
      userId,
      location,
      savedAt: new Date().toISOString(),
      message: "Location saved successfully",
    };
  } catch (error) {
    console.error("Failed to save location:", error);
    throw new Error("Failed to save location");
  }
};

/**
 * @deprecated Use backend preferences API when available
 * Remove saved location
 */
export const removeSavedLocationAPI = async (userId, locationId) => {
  try {
    const currentPrefs = await fetchUserPreferencesAPI(userId);
    const savedLocations = (currentPrefs.savedLocations || []).filter(
      (loc) => loc.id !== locationId
    );

    const updatedPrefs = {
      ...currentPrefs,
      savedLocations,
      updatedAt: new Date().toISOString(),
    };

    localStorage.setItem("user_preferences", JSON.stringify(updatedPrefs));

    return {
      success: true,
      userId,
      locationId,
      removedAt: new Date().toISOString(),
      message: "Location removed successfully",
    };
  } catch (error) {
    console.error("Failed to remove location:", error);
    throw new Error("Failed to remove location");
  }
};

/**
 * @deprecated Use backend search history API when available
 * Add to recent searches
 */
export const addRecentSearchAPI = async (userId, searchTerm) => {
  try {
    const currentPrefs = await fetchUserPreferencesAPI(userId);
    const recentSearches = currentPrefs.recentSearches || [];

    // Remove duplicate and add to front
    const filtered = recentSearches.filter((s) => s !== searchTerm);
    filtered.unshift(searchTerm);

    // Keep only last 10 searches
    const updatedSearches = filtered.slice(0, 10);

    const updatedPrefs = {
      ...currentPrefs,
      recentSearches: updatedSearches,
      updatedAt: new Date().toISOString(),
    };

    localStorage.setItem("user_preferences", JSON.stringify(updatedPrefs));

    return {
      success: true,
      userId,
      searchTerm,
      addedAt: new Date().toISOString(),
    };
  } catch (error) {
    console.error("Failed to add recent search:", error);
    // Don't throw error for non-critical operation
    return {
      success: false,
      userId,
      searchTerm,
    };
  }
};

/**
 * @deprecated Use backend search history API when available
 * Clear recent searches
 */
export const clearRecentSearchesAPI = async (userId) => {
  try {
    const currentPrefs = await fetchUserPreferencesAPI(userId);
    const updatedPrefs = {
      ...currentPrefs,
      recentSearches: [],
      updatedAt: new Date().toISOString(),
    };

    localStorage.setItem("user_preferences", JSON.stringify(updatedPrefs));

    return {
      success: true,
      userId,
      clearedAt: new Date().toISOString(),
      message: "Search history cleared",
    };
  } catch (error) {
    console.error("Failed to clear search history:", error);
    throw new Error("Failed to clear search history");
  }
};

/**
 * @deprecated Mock function - not implemented in backend yet
 * Verify user account
 */
export const verifyUserAccountAPI = async (userId, verificationCode) => {
  // This should be implemented when backend supports verification
  throw new Error("Account verification not implemented yet");
};
