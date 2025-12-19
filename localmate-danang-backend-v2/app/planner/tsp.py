"""TSP Algorithm - Nearest Neighbor + 2-opt optimization.

Optimizes route for a list of places to minimize total travel distance.
Uses Haversine formula for distance calculation.
"""

from math import radians, sin, cos, sqrt, atan2


def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate distance between 2 points on Earth in kilometers.
    
    Uses the Haversine formula for great-circle distance.
    
    Args:
        lat1, lng1: First point coordinates
        lat2, lng2: Second point coordinates
        
    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth's radius in km
    
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c


def calculate_distance_matrix(places: list[dict]) -> list[list[float]]:
    """
    Build NxN distance matrix for all place pairs.
    
    Args:
        places: List of places with 'lat' and 'lng' keys
        
    Returns:
        NxN matrix where matrix[i][j] is distance from place i to j
    """
    n = len(places)
    matrix = [[0.0] * n for _ in range(n)]
    
    for i in range(n):
        for j in range(n):
            if i != j:
                matrix[i][j] = haversine(
                    places[i]['lat'], places[i]['lng'],
                    places[j]['lat'], places[j]['lng']
                )
    
    return matrix


def nearest_neighbor(matrix: list[list[float]], start: int = 0) -> list[int]:
    """
    Greedy nearest neighbor heuristic for TSP.
    
    Builds tour by always visiting the closest unvisited city.
    O(n²) complexity.
    
    Args:
        matrix: Distance matrix
        start: Starting city index
        
    Returns:
        List of city indices in visit order
    """
    n = len(matrix)
    visited = [False] * n
    tour = [start]
    visited[start] = True
    
    for _ in range(n - 1):
        current = tour[-1]
        nearest = -1
        min_dist = float('inf')
        
        for j in range(n):
            if not visited[j] and matrix[current][j] < min_dist:
                min_dist = matrix[current][j]
                nearest = j
        
        if nearest != -1:
            tour.append(nearest)
            visited[nearest] = True
    
    return tour


def two_opt(tour: list[int], matrix: list[list[float]]) -> list[int]:
    """
    2-opt local search improvement for TSP.
    
    Iteratively reverses segments to reduce total distance.
    Continues until no improvement is found.
    
    Args:
        tour: Initial tour (list of indices)
        matrix: Distance matrix
        
    Returns:
        Improved tour
    """
    n = len(tour)
    if n < 4:
        return tour
    
    improved = True
    tour = tour.copy()
    
    while improved:
        improved = False
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                if j == n - 1:
                    # Handle edge case for last element
                    d1 = matrix[tour[i-1]][tour[i]] + matrix[tour[j]][tour[0]]
                    d2 = matrix[tour[i-1]][tour[j]] + matrix[tour[i]][tour[0]]
                else:
                    d1 = matrix[tour[i-1]][tour[i]] + matrix[tour[j]][tour[j+1]]
                    d2 = matrix[tour[i-1]][tour[j]] + matrix[tour[i]][tour[j+1]]
                
                if d2 < d1 - 0.0001:  # Small epsilon to avoid floating point issues
                    # Reverse segment [i, j]
                    tour[i:j+1] = tour[i:j+1][::-1]
                    improved = True
    
    return tour


def calculate_total_distance(tour: list[int], matrix: list[list[float]]) -> float:
    """Calculate total distance of a tour."""
    total = 0.0
    for i in range(len(tour) - 1):
        total += matrix[tour[i]][tour[i+1]]
    return total


def optimize_route(places: list[dict], start_index: int = 0) -> tuple[list[int], float]:
    """
    Main TSP optimization function.
    
    Uses Nearest Neighbor heuristic followed by 2-opt improvement.
    Suitable for up to ~50 places.
    
    Args:
        places: List of places with 'lat' and 'lng' keys
        start_index: Index of starting place (default: first place)
        
    Returns:
        Tuple of (optimized_order, total_distance_km)
        - optimized_order: List of indices in visit order
        - total_distance_km: Total route distance
    """
    n = len(places)
    
    # Handle edge cases
    if n == 0:
        return [], 0.0
    if n == 1:
        return [0], 0.0
    if n == 2:
        dist = haversine(
            places[0]['lat'], places[0]['lng'],
            places[1]['lat'], places[1]['lng']
        )
        return [0, 1], dist
    
    # Build distance matrix
    matrix = calculate_distance_matrix(places)
    
    # Get initial tour using nearest neighbor
    tour = nearest_neighbor(matrix, start_index)
    
    # Improve with 2-opt
    tour = two_opt(tour, matrix)
    
    # Calculate total distance
    total = calculate_total_distance(tour, matrix)
    
    return tour, round(total, 2)


def estimate_duration(distance_km: float, avg_speed_kmh: float = 30) -> int:
    """
    Estimate travel duration in minutes.
    
    Args:
        distance_km: Total distance in km
        avg_speed_kmh: Average speed (default: 30 km/h for city driving)
        
    Returns:
        Estimated duration in minutes
    """
    hours = distance_km / avg_speed_kmh
    return int(hours * 60)
