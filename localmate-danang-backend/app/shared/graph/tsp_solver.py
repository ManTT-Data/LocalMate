"""TSP Solver - Traveling Salesman Problem heuristics."""

from app.shared.utils.geo_utils import haversine_distance


async def nearest_neighbor_tsp(
    points: list[tuple[float, float]],
    start_index: int = 0,
) -> list[int]:
    """
    Solve TSP using Nearest Neighbor heuristic.

    This is a greedy algorithm that always visits the nearest unvisited point.
    Time complexity: O(n²)

    Args:
        points: List of (latitude, longitude) tuples
        start_index: Index to start from (default: 0)

    Returns:
        List of indices representing the visiting order
    """
    n = len(points)

    # Handle trivial cases
    if n <= 2:
        return list(range(n))

    visited = [False] * n
    order = [start_index]
    visited[start_index] = True
    current = start_index

    # Visit all remaining points
    for _ in range(n - 1):
        nearest = None
        min_dist = float("inf")

        # Find nearest unvisited point
        for j in range(n):
            if not visited[j]:
                dist = haversine_distance(points[current], points[j])
                if dist < min_dist:
                    min_dist = dist
                    nearest = j

        if nearest is not None:
            visited[nearest] = True
            order.append(nearest)
            current = nearest

    return order


async def calculate_route_distance(
    points: list[tuple[float, float]],
    order: list[int],
) -> float:
    """
    Calculate total distance for a given route order.

    Args:
        points: List of (latitude, longitude) tuples
        order: List of indices representing visiting order

    Returns:
        Total distance in kilometers
    """
    total = 0.0
    for i in range(len(order) - 1):
        total += haversine_distance(points[order[i]], points[order[i + 1]])
    return total


async def optimize_route(
    points: list[tuple[float, float]],
    start_lat: float | None = None,
    start_lng: float | None = None,
) -> list[int]:
    """
    Optimize visiting order for a list of places.

    If start location is provided, uses it as the first point.

    Args:
        points: List of (latitude, longitude) tuples
        start_lat: Optional starting latitude
        start_lng: Optional starting longitude

    Returns:
        Optimized order of indices
    """
    if not points:
        return []

    # If start location provided, find closest point to start from
    start_index = 0
    if start_lat is not None and start_lng is not None:
        start_point = (start_lat, start_lng)
        min_dist = float("inf")
        for i, point in enumerate(points):
            dist = haversine_distance(start_point, point)
            if dist < min_dist:
                min_dist = dist
                start_index = i

    return await nearest_neighbor_tsp(points, start_index)
