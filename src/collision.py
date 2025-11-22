"""
Proper collision detection for Pokemon Crystal using actual RAM addresses.
Based on pokecrystal disassembly documentation.
"""

def read_collision_around_player(pyboy):
    """
    Read the actual collision data from Pokemon Crystal's RAM.
    
    Addresses:
    - 0xC2FA: Collision data (down)
    - 0xC2FB: Collision data (up)
    - 0xC2FC: Collision data (left)
    - 0xC2FD: Collision data (right)
    
    Returns dict with collision info for each direction.
    """
    collision = {
        'down': pyboy.memory[0xC2FA],
        'up': pyboy.memory[0xC2FB],
        'left': pyboy.memory[0xC2FC],
        'right': pyboy.memory[0xC2FD]
    }
    return collision

def is_direction_walkable(collision_value):
    """
    Determine if a direction is walkable based on collision value.
    0x00 typically means walkable/land tile.
    Other values indicate walls, water, etc.
    """
    # Common collision values:
    # 0x00 = LAND (walkable)
    # 0x01 = WATER
    # 0x02+ = WALL/blocked
    return collision_value == 0x00

def get_walkable_directions(pyboy):
    """Get list of directions the player can currently move."""
    collision = read_collision_around_player(pyboy)
    walkable = []
    
    for direction, value in collision.items():
        if is_direction_walkable(value):
            walkable.append(direction)
    
    return walkable
