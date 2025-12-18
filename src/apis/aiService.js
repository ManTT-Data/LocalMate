/**
 * AI Service - Handles all AI conversation and search functionality
 * Connects to LocalMate backend API for chat, image search, and nearby places
 */

import apiHelper from "../utils/apiHelper";
import { apiUrls } from "../utils/constants";

/**
 * Upload image to Supabase Storage
 * @param {File} imageFile - Image file to upload
 * @param {string} [userId="anonymous"] - User ID for organizing uploads
 * @returns {Promise<Object>} Upload response with URL, path, size, content_type
 *
 * @example
 * const result = await uploadImage(file, "user_123");
 * console.log(result.url); // Supabase public URL
 */
export const uploadImage = async (imageFile, userId = "anonymous") => {
  const formData = new FormData();
  formData.append("file", imageFile);
  formData.append("user_id", userId);

  return await apiHelper.postFormData(apiUrls.upload.image, formData);
};

/**
 * Send a message to the AI chat agent
 * @param {Object} messageData - Chat message data
 * @param {string} messageData.message - User's message in natural language
 * @param {string} [messageData.userId="anonymous"] - User ID for session management
 * @param {string} [messageData.sessionId="default"] - Session ID for conversation history
 * @param {string} [messageData.provider="MegaLLM"] - LLM provider ("Google" or "MegaLLM")
 * @param {string} [messageData.model] - Model name (uses default if not specified)
 * @param {string} [messageData.imageUrl] - Optional image URL for visual search
 * @param {boolean} [messageData.reactMode=false] - Enable ReAct multi-step reasoning
 * @param {number} [messageData.maxSteps=5] - Maximum reasoning steps (1-10)
 * @returns {Promise<Object>} Chat response with workflow information
 *
 * @example
 * const response = await sendMessage({
 *   message: "Quán cafe gần Mỹ Khê",
 *   userId: "user_123",
 *   reactMode: false
 * });
 */
export const sendMessage = async (messageData) => {
  const payload = {
    message: messageData.message,
    user_id: messageData.userId || "anonymous",
    session_id: messageData.sessionId || "default",
    provider: messageData.provider || "MegaLLM",
    ...(messageData.model && { model: messageData.model }),
    ...(messageData.imageUrl && { image_url: messageData.imageUrl }),
    react_mode: messageData.reactMode || false,
    max_steps: messageData.maxSteps || 5,
  };

  return await apiHelper.post(apiUrls.chat.send, payload);
};

/**
 * Clear conversation history for a user
 * @param {string} userId - User ID to clear history for
 * @param {string} [sessionId] - Session ID to clear (clears all if not provided)
 * @returns {Promise<Object>} Status and message
 *
 * @example
 * await clearConversation("user_123", "default");
 */
export const clearConversation = async (userId, sessionId = null) => {
  const payload = {
    user_id: userId,
    ...(sessionId && { session_id: sessionId }),
  };

  return await apiHelper.post(apiUrls.chat.clear, payload);
};

/**
 * Get chat history information for a user
 * @param {string} userId - User ID
 * @returns {Promise<Object>} History info with sessions, current session, message count
 *
 * @example
 * const history = await getChatHistory("user_123");
 * console.log(history.sessions); // ["default", "session_2"]
 */
export const getChatHistory = async (userId) => {
  return await apiHelper.get(apiUrls.chat.history(userId));
};

/**
 * Search places by uploading an image
 * @param {File} imageFile - Image file to search
 * @param {number} [limit=10] - Maximum number of results (1-50)
 * @returns {Promise<Object>} Search results with similarity scores
 *
 * @example
 * const results = await searchByImage(imageFile, 10);
 * results.results.forEach(place => {
 *   console.log(`${place.name} - Similarity: ${place.similarity}`);
 * });
 */
export const searchByImage = async (imageFile, limit = 10) => {
  const formData = new FormData();
  formData.append("image", imageFile);
  formData.append("limit", limit.toString());

  return await apiHelper.postFormData(apiUrls.imageSearch, formData);
};

/**
 * Find nearby places using Neo4j spatial query
 * @param {number} lat - Latitude
 * @param {number} lng - Longitude
 * @param {Object} [options] - Additional options
 * @param {number} [options.maxDistanceKm=5.0] - Maximum distance in kilometers
 * @param {string} [options.category] - Category filter (cafe, restaurant, attraction)
 * @param {number} [options.limit=10] - Maximum results
 * @returns {Promise<Object>} Nearby places with distance information
 *
 * @example
 * const places = await findNearbyPlaces(16.0626442, 108.2462143, {
 *   maxDistanceKm: 3.0,
 *   category: "cafe",
 *   limit: 10
 * });
 */
export const findNearbyPlaces = async (lat, lng, options = {}) => {
  const payload = {
    lat,
    lng,
    max_distance_km: options.maxDistanceKm || 5.0,
    ...(options.category && { category: options.category }),
    limit: options.limit || 10,
  };

  return await apiHelper.post(apiUrls.nearby, payload);
};

export default {
  uploadImage,
  sendMessage,
  clearConversation,
  getChatHistory,
  searchByImage,
  findNearbyPlaces,
};
