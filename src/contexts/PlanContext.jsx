import React, { createContext, useContext, useState, useCallback } from "react";

// Create Context
const PlanContext = createContext();

// Custom Hook
export const usePlan = () => {
  const context = useContext(PlanContext);
  if (!context) {
    throw new Error("usePlan must be used within a PlanProvider");
  }
  return context;
};

// Provider Component
export const PlanProvider = ({ children, initialPlan = null }) => {
  const [plan, setPlan] = useState(() => {
    // Initialize with provided plan or default empty plan
    if (initialPlan) {
      return {
        planId: initialPlan.plan_id || "default-plan",
        items: initialPlan.items || [],
        isOptimized: initialPlan.is_optimized || false,
        isOptimizing: false,
        totalDistanceKm: initialPlan.total_distance_km || 0,
        estimatedDurationMin: initialPlan.estimated_duration_min || 0,
      };
    }

    return {
      planId: "default-plan",
      items: [],
      isOptimized: false,
      isOptimizing: false,
      totalDistanceKm: 0,
      estimatedDurationMin: 0,
    };
  });

  // Add item to plan
  const addItem = useCallback((place) => {
    setPlan((prev) => {
      // Support both old format (id) and new format (place_id)
      const placeId = place.place_id || place.id;

      // Check if item already exists
      const exists = prev.items.some(
        (item) => item.placeId === placeId || item.place_id === placeId
      );
      if (exists) {
        console.log("Item already in plan:", place.name);
        return prev;
      }

      // Handle both formats: {location: {lat, lng}} and {lat, lng}
      const lat = place.lat || place.location?.lat;
      const lng = place.lng || place.location?.lng;

      const newItem = {
        itemId: `item-${Date.now()}`,
        item_id: `item-${Date.now()}`, // Support both naming conventions
        placeId: placeId,
        place_id: placeId, // Support both naming conventions
        name: place.name,
        category: place.category || place.type || "Place",
        lat: lat,
        lng: lng,
        order: prev.items.length,
        addedAt: new Date().toISOString(),
        added_at: new Date(), // Support both naming conventions
        notes: null,
        // Include full place data for rendering
        destination: {
          name: place.name,
          type: place.category || place.type,
          image: place.image,
          rating: place.rating,
          reviews: place.reviews,
          description: place.description,
        },
      };

      return {
        ...prev,
        items: [...prev.items, newItem],
        isOptimized: false,
      };
    });
  }, []);

  // Remove item from plan
  const removeItem = useCallback((itemId) => {
    setPlan((prev) => ({
      ...prev,
      items: prev.items
        .filter((item) => item.itemId !== itemId)
        .map((item, index) => ({ ...item, order: index })),
      isOptimized: false,
    }));
  }, []);

  // Reorder items (for drag & drop)
  const reorderItems = useCallback((newItems) => {
    setPlan((prev) => ({
      ...prev,
      items: newItems.map((item, index) => ({ ...item, order: index })),
      isOptimized: false,
    }));
  }, []);

  // Replace item
  const replaceItem = useCallback((itemId, newPlace) => {
    setPlan((prev) => ({
      ...prev,
      items: prev.items.map((item) =>
        item.itemId === itemId
          ? {
              ...item,
              placeId: newPlace.id,
              name: newPlace.name,
              category: newPlace.type || "Place",
              lat: newPlace.location.lat,
              lng: newPlace.location.lng,
              destination: newPlace,
            }
          : item
      ),
      isOptimized: false,
    }));
  }, []);

  // Optimize route (using GraphHopper Optimization API)
  const optimizeRoute = useCallback(async () => {
    if (plan.items.length < 2) {
      console.warn("Need at least 2 places to optimize");
      return;
    }

    setPlan((prev) => ({ ...prev, isOptimizing: true }));

    try {
      const { optimizeRouteSimple } = await import("../apis/graphhopper");

      // Prepare waypoints for optimization
      const waypoints = prev.items.map((item) => ({
        id: item.itemId,
        name: item.name,
        lat: item.lat,
        lng: item.lng,
      }));

      // Call GraphHopper optimization
      const result = await optimizeRouteSimple(waypoints, "car");

      if (result && result.order) {
        // Reorder items based on optimized order
        const optimizedItems = result.order.map((index) => ({
          ...prev.items[index],
          order: result.order.indexOf(index),
        }));

        setPlan((prev) => ({
          ...prev,
          items: optimizedItems,
          isOptimized: true,
          isOptimizing: false,
          totalDistanceKm: (result.distance / 1000).toFixed(2), // Convert meters to km
          estimatedDurationMin: Math.round((result.distance / 1000 / 40) * 60), // Estimate: 40km/h avg speed
        }));
      } else {
        // Fallback if optimization fails
        setPlan((prev) => ({
          ...prev,
          isOptimized: false,
          isOptimizing: false,
        }));
      }
    } catch (error) {
      console.error("Optimization error:", error);
      setPlan((prev) => ({
        ...prev,
        isOptimized: false,
        isOptimizing: false,
      }));
    }
  }, [plan.items]);

  // Clear plan
  const clearPlan = useCallback(() => {
    setPlan({
      planId: "default-plan",
      items: [],
      isOptimized: false,
      totalDistanceKm: 0,
      estimatedDurationMin: 0,
    });
  }, []);

  const value = {
    plan,
    addItem,
    removeItem,
    reorderItems,
    replaceItem,
    optimizeRoute,
    clearPlan,
  };

  return <PlanContext.Provider value={value}>{children}</PlanContext.Provider>;
};
