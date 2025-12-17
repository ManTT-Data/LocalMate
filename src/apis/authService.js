/**
 * Authentication Service
 * Handles Google OAuth login and logout with backend API
 */

import axios from "axios";
import { baseUrl, apiUrls } from "../utils/constants";

/**
 * Login with Google OAuth access token
 * @param {string} accessToken - Google OAuth access token
 * @returns {Promise<Object>} Login response with user info and JWT token
 */
export const loginWithGoogleAPI = async (accessToken) => {
  try {
    const response = await axios.post(`${baseUrl}${apiUrls.auth.login}`, {
      access_token: accessToken,
    });

    const { user_id, email, full_name, avatar_url, token } = response.data;

    // Store JWT token in localStorage
    if (token) {
      localStorage.setItem("jwt_token", token);
      localStorage.setItem("user_id", user_id);
      localStorage.setItem("user_email", email);
      localStorage.setItem("user_name", full_name);
      if (avatar_url) {
        localStorage.setItem("user_avatar", avatar_url);
      }
    }

    return response.data;
  } catch (error) {
    console.error("Login failed:", error);
    throw new Error(
      error.response?.data?.detail || "Failed to login with Google"
    );
  }
};

/**
 * Logout user
 * @param {string} userId - User ID
 * @returns {Promise<Object>} Logout response
 */
export const logoutAPI = async (userId) => {
  try {
    const response = await axios.post(
      `${baseUrl}${apiUrls.auth.logout}?user_id=${userId}`
    );

    // Clear all user data from localStorage
    localStorage.removeItem("jwt_token");
    localStorage.removeItem("user_id");
    localStorage.removeItem("user_email");
    localStorage.removeItem("user_name");
    localStorage.removeItem("user_avatar");

    return response.data;
  } catch (error) {
    console.error("Logout failed:", error);
    // Even if API call fails, clear local storage
    localStorage.removeItem("jwt_token");
    localStorage.removeItem("user_id");
    localStorage.removeItem("user_email");
    localStorage.removeItem("user_name");
    localStorage.removeItem("user_avatar");

    throw new Error(error.response?.data?.detail || "Failed to logout");
  }
};

/**
 * Check if user is authenticated
 * @returns {boolean} True if user has valid JWT token
 */
export const isAuthenticated = () => {
  return !!localStorage.getItem("jwt_token");
};

/**
 * Get current user info from localStorage
 * @returns {Object|null} User info or null if not logged in
 */
export const getCurrentUser = () => {
  const token = localStorage.getItem("jwt_token");

  if (!token) return null;

  return {
    userId: localStorage.getItem("user_id"),
    email: localStorage.getItem("user_email"),
    fullName: localStorage.getItem("user_name"),
    avatarUrl: localStorage.getItem("user_avatar"),
  };
};

/**
 * Get JWT token for API requests
 * @returns {string|null} JWT token or null
 */
export const getAuthToken = () => {
  return localStorage.getItem("jwt_token");
};
