"""
Python code execution for pathfinding calculations.
Allows the LLM to write and execute pathfinding algorithms.
"""

import heapq
from typing import List, Tuple, Set


def manhattan_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    """Calculate Manhattan distance between two points."""
    return abs(x1 - x2) + abs(y1 - y2)


def astar_pathfind(
    start_x: int,
    start_y: int,
    goal_x: int,
    goal_y: int,
    obstacles: Set[Tuple[int, int]],
    map_width: int,
    map_height: int
) -> List[str]:
    """
    A* pathfinding algorithm.

    Args:
        start_x, start_y: Starting position
        goal_x, goal_y: Target position
        obstacles: Set of (x, y) tuples that are blocked
        map_width, map_height: Map boundaries

    Returns:
        List of directions: ["up", "right", "down", ...]
    """
    # Check if goal is reachable
    if (goal_x, goal_y) in obstacles:
        return []

    if goal_x < 0 or goal_y < 0 or goal_x >= map_width or goal_y >= map_height:
        return []

    # Priority queue: (f_score, g_score, x, y)
    open_set = [(0, 0, start_x, start_y)]
    came_from = {}
    g_score = {(start_x, start_y): 0}

    while open_set:
        _, current_g, x, y = heapq.heappop(open_set)

        # Reached goal
        if x == goal_x and y == goal_y:
            return reconstruct_path(came_from, (x, y), (start_x, start_y))

        # Check all neighbors
        neighbors = [
            (x, y - 1, "up"),
            (x, y + 1, "down"),
            (x - 1, y, "left"),
            (x + 1, y, "right")
        ]

        for nx, ny, direction in neighbors:
            # Check bounds
            if nx < 0 or ny < 0 or nx >= map_width or ny >= map_height:
                continue

            # Check obstacles
            if (nx, ny) in obstacles:
                continue

            # Calculate scores
            tentative_g = current_g + 1
            neighbor_pos = (nx, ny)

            if neighbor_pos not in g_score or tentative_g < g_score[neighbor_pos]:
                g_score[neighbor_pos] = tentative_g
                f_score = tentative_g + manhattan_distance(nx, ny, goal_x, goal_y)
                heapq.heappush(open_set, (f_score, tentative_g, nx, ny))
                came_from[neighbor_pos] = ((x, y), direction)

    # No path found
    return []


def reconstruct_path(
    came_from: dict,
    current: Tuple[int, int],
    start: Tuple[int, int]
) -> List[str]:
    """Reconstruct path from came_from dictionary."""
    path = []

    while current in came_from:
        prev_pos, direction = came_from[current]
        path.append(direction)
        current = prev_pos

        if current == start:
            break

    path.reverse()
    return path


def calculate_path_from_data(pathfinding_data: dict) -> dict:
    """
    Calculate path from pathfinding data dictionary.

    Args:
        pathfinding_data: Dict with player, target, map, npcs, collision_map, etc.

    Returns:
        Dict with path and metadata: {"path": [...], "distance": N, "success": bool}
    """
    player = pathfinding_data['player']
    target = pathfinding_data['target']
    map_info = pathfinding_data['map']

    # Build obstacle set from collision map and NPCs
    obstacles = set()

    # Add NPCs as obstacles
    for npc in pathfinding_data.get('npcs', []):
        obstacles.add((npc['x'], npc['y']))

    # Add blocked tiles from collision map
    collision_map = pathfinding_data.get('collision_map', {})
    for (x, y), is_blocked in collision_map.items():
        if is_blocked:
            obstacles.add((x, y))

    # Run A*
    path = astar_pathfind(
        player['x'], player['y'],
        target['x'], target['y'],
        obstacles,
        map_info['width'], map_info['height']
    )

    result = {
        'path': path,
        'distance': len(path),
        'success': len(path) > 0,
        'start': (player['x'], player['y']),
        'goal': (target['x'], target['y']),
        'obstacles_count': len(obstacles)
    }

    return result


def execute_pathfinding_code(code: str, pathfinding_data: dict) -> dict:
    """
    Safely execute LLM-generated pathfinding code.

    Args:
        code: Python code string from LLM
        pathfinding_data: Game state data

    Returns:
        Result dictionary with path or error
    """
    # Create safe execution environment
    safe_globals = {
        'manhattan_distance': manhattan_distance,
        'astar_pathfind': astar_pathfind,
        'heapq': heapq,
        'data': pathfinding_data,
        '__builtins__': {
            'abs': abs,
            'min': min,
            'max': max,
            'len': len,
            'range': range,
            'enumerate': enumerate,
            'list': list,
            'dict': dict,
            'set': set,
            'tuple': tuple,
            'print': print
        }
    }

    result = {'success': False, 'error': None, 'path': []}

    try:
        # Execute code
        exec(code, safe_globals)

        # Check if 'path' variable was created
        if 'path' in safe_globals:
            path = safe_globals['path']
            result['success'] = True
            result['path'] = path
            result['distance'] = len(path)
        else:
            result['error'] = "Code did not create 'path' variable"

    except Exception as e:
        result['error'] = f"Execution error: {str(e)}"

    return result


def format_path_as_keys(path: List[str]) -> List[str]:
    """
    Convert path directions to actual key presses.

    Args:
        path: List of directions ["up", "down", "left", "right"]

    Returns:
        List of key names compatible with PyBoy
    """
    # In this case, directions are already valid key names
    # But we could add optimizations here (e.g., grouping consecutive moves)
    return path


def simplify_path(path: List[str]) -> str:
    """
    Create a human-readable path description.

    Example: ["up", "up", "up", "right", "right"] -> "3 up, 2 right"
    """
    if not path:
        return "No path"

    simplified = []
    current_dir = None
    count = 0

    for direction in path:
        if direction == current_dir:
            count += 1
        else:
            if current_dir:
                simplified.append(f"{count} {current_dir}")
            current_dir = direction
            count = 1

    # Add last group
    if current_dir:
        simplified.append(f"{count} {current_dir}")

    return ", then ".join(simplified)


# Example usage and testing
if __name__ == "__main__":
    # Test pathfinding
    print("Testing A* pathfinding...")

    # Simple test case
    path = astar_pathfind(
        start_x=0, start_y=0,
        goal_x=5, goal_y=5,
        obstacles={(2, 2), (3, 3)},
        map_width=10, map_height=10
    )

    print(f"Path: {path}")
    print(f"Simplified: {simplify_path(path)}")

    # Test with data structure
    test_data = {
        'player': {'x': 10, 'y': 10, 'facing': 'up'},
        'target': {'x': 15, 'y': 8},
        'map': {'width': 30, 'height': 30},
        'npcs': [{'x': 12, 'y': 9}, {'x': 13, 'y': 9}]
    }

    result = calculate_path_from_data(test_data)
    print(f"\nPathfinding result: {result}")
    print(f"Simplified: {simplify_path(result['path'])}")
