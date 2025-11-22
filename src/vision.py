"""
Vision module for Pokemon Crystal AI.
Uses actual RAM collision data for accurate map representation.
"""

from src.pathfinding import get_path_to_exit, format_path_instructions

# Hardcoded exit locations for maps where warp detection doesn't work
MAP_EXIT_HINTS = {
    (24, 7): [(7, 0), "Stairs at (7,0) - go RIGHT then UP"],  # Player's House 2F
}

def get_warp_data(pyboy):
    """Read warp data for the current map."""
    warps = []
    warp_count = pyboy.memory[0xD4B6]
    
    for i in range(min(warp_count, 16)):
        base = 0xD4B7 + (i * 5)
        y = pyboy.memory[base]
        x = pyboy.memory[base + 1]
        warps.append((x, y))
    
    return warps

def get_npc_positions(pyboy):
    """Get positions of NPCs/objects on the current map."""
    npcs = []
    num_objects = pyboy.memory[0xD4CE]
    
    for i in range(min(num_objects, 16)):
        base = 0xD4CF + (i * 16)
        sprite_id = pyboy.memory[base]
        
        if sprite_id == 0:
            continue
            
        y = pyboy.memory[base + 1]
        x = pyboy.memory[base + 2]
        npcs.append((x, y))
    
    return npcs

def get_collision_data(pyboy):
    """
    Read actual collision data from Pokemon Crystal RAM.
    Returns dict with collision values for each direction.
    """
    return {
        'down': pyboy.memory[0xC2FA],
        'up': pyboy.memory[0xC2FB],
        'left': pyboy.memory[0xC2FC],
        'right': pyboy.memory[0xC2FD]
    }

def get_surroundings_grid(pyboy, radius=3):
    """
    Generate grid view with REAL collision data from RAM.
    """
    player_x = pyboy.memory[0xDCB8]
    player_y = pyboy.memory[0xDCB7]
    map_group = pyboy.memory[0xDCB5]
    map_number = pyboy.memory[0xDCB6]
    map_width = pyboy.memory[0xD4B1]
    map_height = pyboy.memory[0xD4B2]
    
    # Get player facing direction
    direction_byte = pyboy.memory[0xDCBB]
    directions = {0x00: "DOWN ↓", 0x04: "UP ↑", 0x08: "LEFT ←", 0x0C: "RIGHT →"}
    facing = directions.get(direction_byte, f"UNKNOWN(0x{direction_byte:02X})")
    
    # Get actual collision data
    collision = get_collision_data(pyboy)
    
    # Get warps
    warps = get_warp_data(pyboy)
    map_key = (map_group, map_number)
    exit_hint = None
    if map_key in MAP_EXIT_HINTS:
        hardcoded_exit, exit_hint = MAP_EXIT_HINTS[map_key]
        if hardcoded_exit not in warps:
            warps.append(hardcoded_exit)
    
    warp_coords = set(warps)
    
    # Get NPCs
    npcs = get_npc_positions(pyboy)
    npc_coords = set(npcs)
    
    # Build grid
    grid = []
    grid.append("=" * (radius * 2 + 3))
    grid.append(f"GRID VIEW (Map: {map_width}x{map_height}, You: {player_x},{player_y}, Facing: {facing})")
    grid.append("=" * (radius * 2 + 3))
    
    for dy in range(-radius, radius + 1):
        row = []
        for dx in range(-radius, radius + 1):
            tile_x = player_x + dx
            tile_y = player_y + dy
            
            if dx == 0 and dy == 0:
                row.append('P')
            elif (tile_x, tile_y) in npc_coords:
                row.append('N')
            elif (tile_x, tile_y) in warp_coords:
                row.append('E')
            elif tile_x < 0 or tile_y < 0 or tile_x >= map_width or tile_y >= map_height:
                row.append('#')
            else:
                row.append('.')
        
        grid.append(' '.join(row))
    
    grid.append("=" * (radius * 2 + 3))
    
    # Show REAL collision data
    grid.append("COLLISION DATA (from RAM):")
    walkable_dirs = []
    for direction, value in collision.items():
        status = "WALKABLE" if value == 0x00 else f"BLOCKED (0x{value:02X})"
        grid.append(f"  {direction.upper()}: {status}")
        if value == 0x00:
            walkable_dirs.append(direction)
    
    if walkable_dirs:
        grid.append(f"\nYou can move: {', '.join(walkable_dirs).upper()}")
    
    # Show exits
    if warps:
        grid.append(f"\nEXITS: {len(warps)} found")
        closest_exit = min(warps, key=lambda w: abs(w[0] - player_x) + abs(w[1] - player_y))
        
        for wx, wy in warps:
            direction = ""
            if wx < player_x:
                direction = "LEFT"
            elif wx > player_x:
                direction = "RIGHT"
            if wy < player_y:
                direction += " UP" if direction else "UP"
            elif wy > player_y:
                direction += " DOWN" if direction else "DOWN"
            
            grid.append(f"  Exit at ({wx},{wy}) - {direction if direction else 'HERE'}")
        
        # Pathfinding
        path = get_path_to_exit(player_x, player_y, closest_exit[0], closest_exit[1])
        instructions = format_path_instructions(path)
        grid.append(f"\nPATH TO EXIT: {instructions}")
        if len(path) <= 10:
            grid.append(f"Button sequence: {', '.join(path)}")
        
        if exit_hint:
            grid.append(f"HINT: {exit_hint}")
    
    grid.append("\nLegend: P=You, N=NPC, E=EXIT, .=Unknown, #=Out of bounds")
    
    return '\n'.join(grid)





