"""
Pathfinding utilities for Pokemon Crystal AI.
Provides simple A* pathfinding to navigate to exits.
"""

def manhattan_distance(pos1, pos2):
    """Calculate Manhattan distance between two positions."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def get_path_to_exit(player_x, player_y, exit_x, exit_y):
    """
    Calculate the sequence of moves to reach an exit.
    Returns a list of directions: ['right', 'right', 'up', 'up', ...]
    
    Uses simple greedy pathfinding (move closer on each axis).
    """
    path = []
    current_x, current_y = player_x, player_y
    
    # Move horizontally first
    while current_x != exit_x:
        if current_x < exit_x:
            path.append('right')
            current_x += 1
        else:
            path.append('left')
            current_x -= 1
    
    # Then move vertically
    while current_y != exit_y:
        if current_y < exit_y:
            path.append('down')
            current_y += 1
        else:
            path.append('up')
            current_y -= 1
    
    return path

def format_path_instructions(path):
    """
    Format a path into human-readable instructions.
    Example: ['right', 'right', 'up'] -> "Go RIGHT 2 times, then UP 1 time"
    """
    if not path:
        return "You are at the exit!"
    
    # Count consecutive moves
    instructions = []
    current_dir = None
    count = 0
    
    for direction in path:
        if direction == current_dir:
            count += 1
        else:
            if current_dir:
                instructions.append(f"{current_dir.upper()} {count} time{'s' if count > 1 else ''}")
            current_dir = direction
            count = 1
    
    # Add last direction
    if current_dir:
        instructions.append(f"{current_dir.upper()} {count} time{'s' if count > 1 else ''}")
    
    return "Go " + ", then ".join(instructions)
