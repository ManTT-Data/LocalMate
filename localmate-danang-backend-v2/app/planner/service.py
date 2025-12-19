"""Trip Planner Service - Business logic and in-memory storage."""

import uuid
from datetime import datetime
from typing import Optional
from collections import defaultdict

from app.planner.models import Plan, PlanItem, PlaceInput
from app.planner.tsp import optimize_route, estimate_duration, haversine


class PlannerService:
    """
    Service for managing trip plans.
    
    Uses in-memory storage per user_id (session-based).
    Plans persist during server lifetime.
    """
    
    def __init__(self):
        """Initialize with in-memory storage."""
        # {user_id: {plan_id: Plan}}
        self._plans: dict[str, dict[str, Plan]] = defaultdict(dict)
    
    def create_plan(self, user_id: str, name: str = "My Trip") -> Plan:
        """
        Create a new empty plan.
        
        Args:
            user_id: Owner's user ID
            name: Plan name
            
        Returns:
            Created Plan object
        """
        plan_id = f"plan_{uuid.uuid4().hex[:12]}"
        
        plan = Plan(
            plan_id=plan_id,
            user_id=user_id,
            name=name,
            items=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        self._plans[user_id][plan_id] = plan
        return plan
    
    def get_plan(self, user_id: str, plan_id: str) -> Optional[Plan]:
        """Get a plan by ID."""
        return self._plans.get(user_id, {}).get(plan_id)
    
    def get_user_plans(self, user_id: str) -> list[Plan]:
        """Get all plans for a user."""
        return list(self._plans.get(user_id, {}).values())
    
    def get_or_create_default_plan(self, user_id: str) -> Plan:
        """Get user's first plan or create one."""
        plans = self.get_user_plans(user_id)
        if plans:
            return plans[0]
        return self.create_plan(user_id)
    
    def add_place(
        self,
        user_id: str,
        plan_id: str,
        place: PlaceInput,
        notes: Optional[str] = None
    ) -> Optional[PlanItem]:
        """
        Add a place to a plan.
        
        Args:
            user_id: Owner's user ID
            plan_id: Target plan ID
            place: Place data
            notes: Optional user notes
            
        Returns:
            Created PlanItem or None if plan not found
        """
        plan = self.get_plan(user_id, plan_id)
        if not plan:
            return None
        
        # Create new item
        item_id = f"item_{uuid.uuid4().hex[:8]}"
        order = len(plan.items) + 1
        
        item = PlanItem(
            item_id=item_id,
            place_id=place.place_id,
            name=place.name,
            category=place.category,
            lat=place.lat,
            lng=place.lng,
            order=order,
            added_at=datetime.now(),
            notes=notes,
            rating=place.rating,
        )
        
        plan.items.append(item)
        plan.updated_at = datetime.now()
        plan.is_optimized = False
        
        # Update distance if there are multiple items
        self._update_distances(plan)
        
        return item
    
    def remove_place(self, user_id: str, plan_id: str, item_id: str) -> bool:
        """
        Remove a place from plan.
        
        Returns:
            True if removed, False if not found
        """
        plan = self.get_plan(user_id, plan_id)
        if not plan:
            return False
        
        # Find and remove item
        original_len = len(plan.items)
        plan.items = [item for item in plan.items if item.item_id != item_id]
        
        if len(plan.items) < original_len:
            # Reorder remaining items
            for i, item in enumerate(plan.items):
                item.order = i + 1
            
            plan.updated_at = datetime.now()
            plan.is_optimized = False
            self._update_distances(plan)
            return True
        
        return False
    
    def reorder_places(self, user_id: str, plan_id: str, new_order: list[str]) -> bool:
        """
        Reorder places in plan.
        
        Args:
            user_id: Owner's user ID
            plan_id: Plan ID
            new_order: List of item_ids in new order
            
        Returns:
            True if reordered, False if invalid
        """
        plan = self.get_plan(user_id, plan_id)
        if not plan:
            return False
        
        # Validate all item_ids exist
        existing_ids = {item.item_id for item in plan.items}
        if set(new_order) != existing_ids:
            return False
        
        # Create id -> item mapping
        item_map = {item.item_id: item for item in plan.items}
        
        # Reorder
        plan.items = [item_map[item_id] for item_id in new_order]
        for i, item in enumerate(plan.items):
            item.order = i + 1
        
        plan.updated_at = datetime.now()
        plan.is_optimized = False
        self._update_distances(plan)
        
        return True
    
    def replace_place(
        self,
        user_id: str,
        plan_id: str,
        item_id: str,
        new_place: PlaceInput
    ) -> Optional[PlanItem]:
        """
        Replace a place in plan with a new one.
        
        Args:
            user_id: Owner's user ID
            plan_id: Plan ID
            item_id: Item to replace
            new_place: New place data
            
        Returns:
            Updated PlanItem or None if not found
        """
        plan = self.get_plan(user_id, plan_id)
        if not plan:
            return None
        
        # Find item to replace
        for i, item in enumerate(plan.items):
            if item.item_id == item_id:
                # Update with new place data
                item.place_id = new_place.place_id
                item.name = new_place.name
                item.category = new_place.category
                item.lat = new_place.lat
                item.lng = new_place.lng
                item.rating = new_place.rating
                
                plan.updated_at = datetime.now()
                plan.is_optimized = False
                self._update_distances(plan)
                
                return item
        
        return None
    
    def optimize_plan(self, user_id: str, plan_id: str, start_index: int = 0) -> Optional[Plan]:
        """
        Optimize the route for a plan using TSP.
        
        Args:
            user_id: Owner's user ID
            plan_id: Plan ID
            start_index: Index of starting place
            
        Returns:
            Optimized Plan or None if not found
        """
        plan = self.get_plan(user_id, plan_id)
        if not plan or len(plan.items) < 2:
            return plan
        
        # Calculate original distance for comparison
        original_distance = plan.total_distance_km or 0
        
        # Convert items to places format for TSP
        places = [
            {'lat': item.lat, 'lng': item.lng}
            for item in plan.items
        ]
        
        # Run TSP optimization
        optimized_order, total_distance = optimize_route(places, start_index)
        
        # Reorder items according to optimized order
        original_items = plan.items.copy()
        plan.items = [original_items[i] for i in optimized_order]
        
        # Update orders
        for i, item in enumerate(plan.items):
            item.order = i + 1
        
        # Update plan metadata
        plan.total_distance_km = total_distance
        plan.estimated_duration_min = estimate_duration(total_distance)
        plan.is_optimized = True
        plan.updated_at = datetime.now()
        
        # Calculate distances between consecutive items
        self._update_distances(plan)
        
        return plan
    
    def _update_distances(self, plan: Plan) -> None:
        """Update total distance and per-item distances."""
        if len(plan.items) < 2:
            plan.total_distance_km = 0
            plan.estimated_duration_min = 0
            if plan.items:
                plan.items[0].distance_from_prev_km = None
            return
        
        total = 0.0
        plan.items[0].distance_from_prev_km = None
        
        for i in range(1, len(plan.items)):
            prev = plan.items[i - 1]
            curr = plan.items[i]
            
            dist = haversine(prev.lat, prev.lng, curr.lat, curr.lng)
            curr.distance_from_prev_km = round(dist, 2)
            total += dist
        
        plan.total_distance_km = round(total, 2)
        plan.estimated_duration_min = estimate_duration(total)
    
    def delete_plan(self, user_id: str, plan_id: str) -> bool:
        """Delete a plan."""
        if plan_id in self._plans.get(user_id, {}):
            del self._plans[user_id][plan_id]
            return True
        return False


# Global singleton instance
planner_service = PlannerService()
