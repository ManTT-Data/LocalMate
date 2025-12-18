/**
 * Planner Service - Trip Planning and Optimization API
 * Handles plan creation, optimization, and route management
 */

import apiHelper from "../utils/apiHelper";
import { apiUrls, HARDCODED_TEST_USER } from "../utils/constants";

/**
 * Create a new plan
 * @param {Object} planData - Plan data
 * @param {string} userId - User ID
 * @returns {Promise<Object>} Created plan
 */
export const createPlannerPlan = async (planData, userId) => {
  const { title, places = [] } = planData;

  const request = {
    title,
    places: places.map((place) => ({
      place_id: place.place_id || place.id,
      name: place.name,
      lat: place.lat,
      lng: place.lng,
      category: place.category,
    })),
  };

  const response = await apiHelper.post(
    `${apiUrls.planner.create}?user_id=${userId}`,
    request
  );

  return response;
};

/**
 * Get user's plans
 * @param {string} userId - User ID
 * @returns {Promise<Array>} List of plans
 */
export const getUserPlans = async (userId) => {
  const response = await apiHelper.get(
    `${apiUrls.planner.getUserPlans}?user_id=${userId}`
  );
  return response;
};

/**
 * Get a specific plan
 * @param {string} planId - Plan ID
 * @param {string} userId - User ID
 * @returns {Promise<Object>} Plan details
 */
export const getPlan = async (planId, userId) => {
  const response = await apiHelper.get(
    `${apiUrls.planner.get(planId)}?user_id=${userId}`
  );
  return response;
};

/**
 * Delete a plan
 * @param {string} planId - Plan ID
 * @param {string} userId - User ID
 * @returns {Promise<Object>} Delete result
 */
export const deletePlannerPlan = async (planId, userId) => {
  const response = await apiHelper.delete(
    `${apiUrls.planner.delete(planId)}?user_id=${userId}`
  );
  return response;
};

/**
 * Add a place to a plan
 * @param {string} planId - Plan ID
 * @param {Object} placeData - Place data
 * @param {string} userId - User ID
 * @returns {Promise<Object>} Add result
 */
export const addPlaceToPlan = async (planId, placeData, userId) => {
  const request = {
    place_id: placeData.place_id || placeData.id,
    name: placeData.name,
    lat: placeData.lat,
    lng: placeData.lng,
    category: placeData.category,
  };

  const response = await apiHelper.post(
    `${apiUrls.planner.add(planId)}?user_id=${userId}`,
    request
  );

  return response;
};

/**
 * Remove a place from a plan
 * @param {string} planId - Plan ID
 * @param {string} itemId - Item ID to remove
 * @param {string} userId - User ID
 * @returns {Promise<Object>} Remove result
 */
export const removePlaceFromPlan = async (planId, itemId, userId) => {
  const response = await apiHelper.delete(
    `${apiUrls.planner.remove(planId, itemId)}?user_id=${userId}`
  );
  return response;
};

/**
 * Reorder places in a plan
 * @param {string} planId - Plan ID
 * @param {Array<string>} order - New order of item IDs
 * @param {string} userId - User ID
 * @returns {Promise<Object>} Reorder result
 */
export const reorderPlan = async (planId, order, userId) => {
  const request = { order };

  const response = await apiHelper.post(
    `${apiUrls.planner.reorder(planId)}?user_id=${userId}`,
    request
  );

  return response;
};

/**
 * Optimize a plan's route
 * @param {string} planId - Plan ID
 * @param {string} userId - User ID (defaults to test user)
 * @returns {Promise<Object>} Optimized plan with routes
 */
export const optimizePlan = async (
  planId,
  userId = HARDCODED_TEST_USER.userId
) => {
  const response = await apiHelper.post(
    `${apiUrls.planner.optimize(planId)}?user_id=${userId}`
  );

  return response;
};

/**
 * Replace a place in a plan
 * @param {string} planId - Plan ID
 * @param {string} itemId - Item ID to replace
 * @param {Object} newPlaceData - New place data
 * @param {string} userId - User ID
 * @returns {Promise<Object>} Replace result
 */
export const replacePlaceInPlan = async (
  planId,
  itemId,
  newPlaceData,
  userId
) => {
  const request = {
    place_id: newPlaceData.place_id || newPlaceData.id,
    name: newPlaceData.name,
    lat: newPlaceData.lat,
    lng: newPlaceData.lng,
    category: newPlaceData.category,
  };

  const response = await apiHelper.post(
    `${apiUrls.planner.replace(planId, itemId)}?user_id=${userId}`,
    request
  );

  return response;
};

// Export all functions
export default {
  createPlannerPlan,
  getUserPlans,
  getPlan,
  deletePlannerPlan,
  addPlaceToPlan,
  removePlaceFromPlan,
  reorderPlan,
  optimizePlan,
  replacePlaceInPlan,
};
