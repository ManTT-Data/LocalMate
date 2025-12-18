/**
 * AI Places Store - Shared state for AI-suggested places
 * Used to share places between ChatPanel and MapPanel
 */

import { create } from "zustand";

const useAiPlacesStore = create((set) => ({
  // AI-suggested places from chat responses
  aiPlaces: [],

  // Set AI places from new chat response
  setAiPlaces: (places) => {
    set({ aiPlaces: places || [] });
  },

  // Add places to existing list (for accumulation)
  addAiPlaces: (places) => {
    set((state) => ({
      aiPlaces: [...state.aiPlaces, ...(places || [])],
    }));
  },

  // Clear all AI places
  clearAiPlaces: () => {
    set({ aiPlaces: [] });
  },

  // Remove a specific place by ID
  removeAiPlace: (placeId) => {
    set((state) => ({
      aiPlaces: state.aiPlaces.filter((p) => p.place_id !== placeId),
    }));
  },
}));

export default useAiPlacesStore;
