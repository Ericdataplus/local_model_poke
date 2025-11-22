"""
Complete memory reading for Pokemon Crystal.
Reads all relevant game state including facing direction, map data, etc.
"""

def get_player_direction(pyboy):
    """
    Get the direction the player is facing.
    0x00 = Down, 0x04 = Up, 0x08 = Left, 0x0C = Right
    """
    direction_byte = pyboy.memory[0xDCBB]
    directions = {
        0x00: "DOWN",
        0x04: "UP",
        0x08: "LEFT",
        0x0C: "RIGHT"
    }
    return directions.get(direction_byte, f"UNKNOWN(0x{direction_byte:02X})")

def get_map_blocks(pyboy):
    """
    Read the current map's block data.
    Map blocks start at 0xC800 and go to 0xCD13 (1300 bytes).
    """
    map_width = pyboy.memory[0xD4B1]
    map_height = pyboy.memory[0xD4B2]
    
    # Read map blocks
    blocks = []
    for i in range(min(map_width * map_height, 1300)):
        block_id = pyboy.memory[0xC800 + i]
        blocks.append(block_id)
    
    return blocks, map_width, map_height

def get_movement_permissions(pyboy):
    """
    Read movement permissions byte.
    This tells us if the player can move or is in a cutscene/menu.
    """
    return pyboy.memory[0xD4DB]

def get_complete_game_state(pyboy):
    """
    Get ALL relevant game state data.
    """
    state = {}
    
    # Basic position
    state['x'] = pyboy.memory[0xDCB8]
    state['y'] = pyboy.memory[0xDCB7]
    state['map_group'] = pyboy.memory[0xDCB5]
    state['map_number'] = pyboy.memory[0xDCB6]
    
    # Map info
    state['map_width'] = pyboy.memory[0xD4B1]
    state['map_height'] = pyboy.memory[0xD4B2]
    
    # Player state
    state['facing'] = get_player_direction(pyboy)
    state['party_count'] = pyboy.memory[0xDCD7]
    state['movement_permissions'] = get_movement_permissions(pyboy)
    
    # Collision data (adjacent tiles)
    state['collision'] = {
        'down': pyboy.memory[0xC2FA],
        'up': pyboy.memory[0xC2FB],
        'left': pyboy.memory[0xC2FC],
        'right': pyboy.memory[0xC2FD]
    }
    
    # Warp data
    state['warp_count'] = pyboy.memory[0xD4B6]
    
    # NPC/Object count
    state['object_count'] = pyboy.memory[0xD4CE]
    
    return state
