"""
Markdown table-based vision system for Pokemon Crystal AI.
Provides structured map data that LLMs can easily parse and analyze.
"""

def create_map_table(pyboy, radius=5):
    """
    Create a markdown table representation of the map around the player.

    Args:
        pyboy: PyBoy instance
        radius: How many tiles to show in each direction

    Returns:
        Markdown formatted table string with map data
    """
    # Get player position - Pokemon Crystal specific addresses
    player_x = pyboy.memory[0xDCB8]  # X coordinate (confirmed working)
    player_y = pyboy.memory[0xDCB7]  # Y coordinate (confirmed working)

    # Map dimensions - try multiple addresses for Pokemon Crystal
    # The addresses 0xD4B1/0xD4B2 are giving wrong values (140x80)
    map_width_raw = pyboy.memory[0xD4B1]
    map_height_raw = pyboy.memory[0xD4B2]

    # Pokemon Crystal map header is at different location
    # Try reading from map header directly
    map_width_alt = pyboy.memory[0xD4B3]  # Alternate width
    map_height_alt = pyboy.memory[0xD4B4]  # Alternate height

    # DEBUG: Print both attempts
    print(f"[DEBUG] Player position: ({player_x}, {player_y})")
    print(f"[DEBUG] Map dimensions (0xD4B1/B2): {map_width_raw}x{map_height_raw}")
    print(f"[DEBUG] Map dimensions (0xD4B3/B4): {map_width_alt}x{map_height_alt}")

    # Use the smaller, more reasonable value (Player's House 2F is small)
    # Typically 4-10 tiles wide/tall for interior maps
    if map_width_alt < map_width_raw and map_width_alt > 0 and map_width_alt < 32:
        map_width = map_width_alt
        map_height = map_height_alt
        print(f"[DEBUG] Using alternate map dimensions: {map_width}x{map_height}")
    else:
        # If both seem wrong, cap at reasonable size
        map_width = min(map_width_raw, 32)
        map_height = min(map_height_raw, 32)
        print(f"[DEBUG] Using capped map dimensions: {map_width}x{map_height}")

    # Get player facing direction
    direction_byte = pyboy.memory[0xDCBB]

    # DEBUG: Show actual direction byte if unmapped
    known_bytes = [0x00, 0x01, 0x04, 0x05, 0x08, 0x09, 0x0C, 0x0D, 0x1F]
    if direction_byte not in known_bytes:
        print(f"[DEBUG] Unknown direction byte: 0x{direction_byte:02X}")

    direction_arrows = {
        0x00: "↓",  # DOWN
        0x04: "↑",  # UP
        0x08: "←",  # LEFT
        0x0C: "→",  # RIGHT
        # Pokemon Crystal sometimes uses different values during movement
        0x01: "↓",  # DOWN (moving)
        0x05: "↑",  # UP (moving)
        0x09: "←",  # LEFT (moving)
        0x0D: "→",  # RIGHT (moving)
        0x1F: "🧍"  # Standing still / turning / between actions
    }
    player_arrow = direction_arrows.get(direction_byte, "🧍")

    # Get warps (exits/doors/stairs)
    warps = get_warp_positions(pyboy)
    warp_set = set(warps)

    # Get NPCs
    npcs = get_npc_positions(pyboy)
    npc_set = set(npcs)

    # Get collision data for tiles around player
    collision_map = get_collision_map(pyboy, player_x, player_y, radius, map_width, map_height)

    # Build table header
    table = ["## Map View", ""]
    table.append(f"**Player Position:** ({player_x}, {player_y})")
    table.append(f"**Map Size:** {map_width}x{map_height}")
    table.append("")

    # Create column headers (X coordinates)
    header = "| Y\\X |"
    separator = "|-----|"

    for dx in range(-radius, radius + 1):
        x_coord = player_x + dx
        header += f" {x_coord} |"
        separator += "---|"

    table.append(header)
    table.append(separator)

    # Create rows (Y coordinates)
    for dy in range(-radius, radius + 1):
        y_coord = player_y + dy
        row = f"| **{y_coord}** |"

        for dx in range(-radius, radius + 1):
            x_coord = player_x + dx

            # Determine tile type - PRIORITY ORDER MATTERS!
            if dx == 0 and dy == 0:
                # Player position - show arrow indicating direction
                cell = player_arrow
            elif (x_coord, y_coord) in warp_set:
                # Exit/Door/Stairs - ALWAYS show (high priority)
                cell = "🚪"
            elif (x_coord, y_coord) in npc_set:
                # NPC/Object - ALWAYS show (high priority)
                cell = "👤"
            elif x_coord < 0 or y_coord < 0 or x_coord >= map_width or y_coord >= map_height:
                # Out of bounds
                cell = "⬛"
            else:
                # Check collision status
                collision_status = collision_map.get((x_coord, y_coord), 'unknown')

                if collision_status == 'unknown':
                    # Unknown collision - show as gray (uncertain)
                    cell = "▫️"
                elif collision_status:
                    # Blocked/Obstacle - show walls, rocks, etc.
                    cell = "🟫"
                else:
                    # Walkable - empty floor
                    cell = "⬜"

            row += f" {cell} |"

        table.append(row)

    # Add legend
    table.append("")
    table.append("**Legend:**")
    table.append("- ↑↓←→ Player (YOU) - Arrow shows facing direction")
    table.append("- 🚪 Exit/Door/Stairs - Where you can leave the room")
    table.append("- 👤 NPC/Object - People or items to interact with")
    table.append("- ⬜ Walkable - Confirmed you can move here")
    table.append("- 🟫 Obstacle - BLOCKED (walls, furniture, etc.)")
    table.append("- ▫️ Unknown - Not certain if walkable or blocked")
    table.append("- ⬛ Out of bounds - Beyond map edge")

    return "\n".join(table)


def get_warp_positions(pyboy):
    """
    Get all warp/exit positions on current map.
    Pokemon Crystal stores warps differently than Red/Blue.
    """
    # CHECK MANUAL WARPS FIRST - they're 100% reliable
    map_group = pyboy.memory[0xDCB5]
    map_number = pyboy.memory[0xDCB6]
    
    manual_warps = {
        (1, 1): [(7, 0)],     # Player's House 2F
        (1, 2): [(9, 0), (6, 7)], # Player's House 1F (Stairs + Front Door)
        (3, 1): [(4, 7)],     # Rival's House 2F
        (2, 1): [(3, 11)],    # Professor Elm's Lab
        (24, 7): [(7, 0)],    # Player's House 2F (alternate ID)
        (24, 6): [(6, 7)],    # Player's House 1F (alternate ID)
    }
    
    key = (map_group, map_number)
    if key in manual_warps:
        print(f"[DEBUG] ✓ Using MANUAL warp for map {key}: {manual_warps[key]}")
        return manual_warps[key]
    
    # If not a known map, try RAM reading (often unreliable)
    warps = []

    # Try multiple possible warp count addresses for Pokemon Crystal
    warp_addresses = [
        (0xD4B6, 0xD4B7, "Primary"),      # Standard address
        (0xD4EC, 0xD4ED, "Alternate 1"),  # Pokemon Crystal alternate
        (0xD197, 0xD198, "Alternate 2"),  # Another possible location
    ]

    for count_addr, data_addr, label in warp_addresses:
        warp_count = pyboy.memory[count_addr]
        print(f"[DEBUG] Warp count at 0x{count_addr:04X} ({label}): {warp_count}")

        if warp_count > 0 and warp_count <= 16:
            # This looks like a valid warp count
            for i in range(warp_count):
                # Pokemon Crystal warp format: Y, X, warp_id, map_bank, map_id (5 bytes each)
                base = data_addr + (i * 5)
                y = pyboy.memory[base]
                x = pyboy.memory[base + 1]

                # Sanity check: coordinates should be reasonable
                if x < 255 and y < 255:  # Valid coordinates
                    print(f"[DEBUG] Warp {i}: x={x}, y={y} (from base 0x{base:04X})")
                    warps.append((x, y))

            if warps:
                print(f"[DEBUG] Total warps found using {label}: {len(warps)}")
                return warps  # Found valid warps, return them
            else:
                print(f"[DEBUG] No valid warps from {label}, trying next address")
                warps = []  # Clear and try next address

    # If no warps found from any address, try manual detection for specific maps
    # Get current map ID
    map_group = pyboy.memory[0xDCB5]
    map_number = pyboy.memory[0xDCB6]

    print(f"[DEBUG] Current map: group={map_group}, number={map_number}")

    # Manual warp definitions for common starting locations
    # EXPANDED: More specific map detection
    manual_warps = {
        (1, 1): [(7, 0)],     # Player's House 2F - stairs at (7, 0)
        (1, 2): [(9, 0)],     # Player's House 1F - door out
        (3, 1): [(4, 7)],     # Rival's House 2F
        (2, 1): [(3, 11)],    # Professor Elm's Lab
        (24, 7): [(7, 0)],    # Player's House 2F (alternate detection) - Using map bank/number from state
    }

    # Try using map_group and map_number first
    key = (map_group, map_number)
    if key in manual_warps:
        warps = manual_warps[key]
        print(f"[DEBUG] Using manual warp definition for map group/number {key}: {warps}")

    # If STILL no warps and we're clearly in Player's House 2F based on location name
    # (the game state shows "Player's House 2F (24, 7)")
    # Force the stairs to show at (7, 0)
    if not warps:
        # Get current map bank and number from alternate addresses
        map_bank_alt = pyboy.memory[0xDCB5]
        map_num_alt = pyboy.memory[0xDCB6]

        print(f"[DEBUG] No warps detected, checking if we're in a known starting location...")
        print(f"[DEBUG] Map bank/num from alt: ({map_bank_alt}, {map_num_alt})")

        # If warp detection is completely broken, at least show stairs in Player's House 2F
        # We know from the state that map is "(24, 7)" which is Player's House 2F
        # So force stairs at (7, 0) as a last resort
        if map_bank_alt == 24 and map_num_alt == 7:
            warps = [(7, 0)]
            print(f"[DEBUG] FORCED manual warp for Player's House 2F at (7, 0)")
        elif map_bank_alt == 1 and map_num_alt == 1:
            warps = [(7, 0)]
            print(f"[DEBUG] FORCED manual warp for map (1,1) at (7, 0)")
        else:
            # Ultimate fallback: if player X is around 3 and Y is around 3, assume Player's House 2F
            player_x_check = pyboy.memory[0xDCB8]
            player_y_check = pyboy.memory[0xDCB7]
            if 1 <= player_x_check <= 7 and 1 <= player_y_check <= 7:
                # Small map, player in corner area - probably Player's House 2F
                warps = [(7, 0)]
                print(f"[DEBUG] ULTIMATE FALLBACK: Assuming Player's House 2F, adding stairs at (7, 0)")

    print(f"[DEBUG] Final total warps: {len(warps)}")
    return warps


def get_npc_positions(pyboy):
    """Get all NPC/object positions on current map."""
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


def get_collision_map(pyboy, center_x, center_y, radius, map_width, map_height):
    """
    Create a collision map for tiles around the player.
    Returns dict: {(x, y): is_blocked OR 'unknown'}

    Uses actual collision attribute data from Pokemon Crystal's tileset system.
    """
    collision_map = {}

    # Get current collision data for adjacent tiles (MOST ACCURATE)
    current_collision = {
        'down': pyboy.memory[0xC2FA],
        'up': pyboy.memory[0xC2FB],
        'left': pyboy.memory[0xC2FC],
        'right': pyboy.memory[0xC2FD]
    }

    # DEBUG: Print collision values
    print(f"[DEBUG] Collision at ({center_x}, {center_y}): down=0x{current_collision['down']:02X}, up=0x{current_collision['up']:02X}, left=0x{current_collision['left']:02X}, right=0x{current_collision['right']:02X}")

    # Mark adjacent tiles based on REAL collision data
    # 0x00 = walkable, anything else = blocked
    collision_map[(center_x, center_y - 1)] = (current_collision['up'] != 0x00)      # UP
    collision_map[(center_x, center_y + 1)] = (current_collision['down'] != 0x00)    # DOWN
    collision_map[(center_x - 1, center_y)] = (current_collision['left'] != 0x00)    # LEFT
    collision_map[(center_x + 1, center_y)] = (current_collision['right'] != 0x00)   # RIGHT

    # For non-adjacent tiles, use Pokemon Crystal's collision attribute system
    # Each block has a collision byte stored in tileset data
    try:
        # Get tileset collision data pointer
        # Pokemon Crystal stores collision attributes differently than Red/Blue
        tileset_collision_ptr = 0xD3D1  # Tileset collision data pointer

        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                x = center_x + dx
                y = center_y + dy

                # Skip if already have data (adjacent tiles are most accurate)
                if (x, y) in collision_map:
                    continue

                # Check if in bounds
                if x < 0 or y < 0 or x >= map_width or y >= map_height:
                    collision_map[(x, y)] = True  # Out of bounds = blocked
                    continue

                # Read map block ID from current map
                block_index = y * map_width + x

                if block_index < 1024:  # Reasonable map size limit
                    # Get the block ID from map data (0xC800 is overworld map blocks)
                    block_id = pyboy.memory[0xC800 + block_index]

                    # Get collision attribute for this block
                    # Collision attributes stored at 0xD3D1 + block_id
                    # 0 = walkable, non-zero = blocked
                    try:
                        collision_attr = pyboy.memory[tileset_collision_ptr + block_id]

                        # Mark as blocked if collision attribute is non-zero
                        is_blocked = (collision_attr != 0x00)
                        collision_map[(x, y)] = is_blocked

                        # DEBUG: Print a few samples
                        if abs(dx) <= 2 and abs(dy) <= 2:  # Only log nearby tiles
                            print(f"[DEBUG] Tile ({x},{y}): block_id=0x{block_id:02X}, collision_attr=0x{collision_attr:02X}, blocked={is_blocked}")
                    except:
                        # If reading collision attr fails, mark as unknown
                        collision_map[(x, y)] = 'unknown'
                else:
                    # Mark distant tiles as unknown rather than guessing
                    collision_map[(x, y)] = 'unknown'

    except Exception as e:
        # If reading fails, mark unknowns explicitly
        print(f"[DEBUG] Collision map reading failed: {e}")
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                x = center_x + dx
                y = center_y + dy
                if (x, y) not in collision_map:
                    collision_map[(x, y)] = 'unknown'

    return collision_map


def create_pathfinding_data(pyboy, target_x, target_y, radius=10):
    """
    Create structured data for Python pathfinding calculations.
    Returns JSON-like dict with all necessary pathfinding info.
    """
    player_x = pyboy.memory[0xDCB8]
    player_y = pyboy.memory[0xDCB7]
    map_width = pyboy.memory[0xD4B1]
    map_height = pyboy.memory[0xD4B2]

    # Get facing direction
    direction_byte = pyboy.memory[0xDCBB]
    directions = {0x00: "down", 0x04: "up", 0x08: "left", 0x0C: "right"}
    facing = directions.get(direction_byte, "down")

    # Get warps and NPCs
    warps = get_warp_positions(pyboy)
    npcs = get_npc_positions(pyboy)

    # Get collision data (adjacent only)
    collision = {
        'down': pyboy.memory[0xC2FA] != 0x00,
        'up': pyboy.memory[0xC2FB] != 0x00,
        'left': pyboy.memory[0xC2FC] != 0x00,
        'right': pyboy.memory[0xC2FD] != 0x00
    }

    # Get full collision map for pathfinding
    collision_map = get_collision_map(pyboy, player_x, player_y, radius, map_width, map_height)

    data = {
        'player': {
            'x': player_x,
            'y': player_y,
            'facing': facing
        },
        'target': {
            'x': target_x,
            'y': target_y
        },
        'map': {
            'width': map_width,
            'height': map_height
        },
        'warps': [{'x': x, 'y': y} for x, y in warps],
        'npcs': [{'x': x, 'y': y} for x, y in npcs],
        'collision': {
            'adjacent': collision
        },
        'collision_map': collision_map  # Full collision map for A*
    }

    return data


def format_pathfinding_prompt(pyboy, target_x, target_y):
    """
    Create a complete prompt for LLM pathfinding with Python code execution.
    """
    data = create_pathfinding_data(pyboy, target_x, target_y)

    prompt = f"""## Pathfinding Request

Calculate the optimal path from player position to target.

**Current State:**
- Player: ({data['player']['x']}, {data['player']['y']}) facing {data['player']['facing']}
- Target: ({data['target']['x']}, {data['target']['y']})
- Map Size: {data['map']['width']}x{data['map']['height']}

**Obstacles:**
- NPCs at: {[f"({npc['x']},{npc['y']})" for npc in data['npcs']]}
- Adjacent collision: {data['collision']['adjacent']}

**Available Exits:**
{chr(10).join([f"- Exit at ({w['x']}, {w['y']})" for w in data['warps']])}

**Instructions:**
Use Python to calculate A* path. Return as JSON:
{{"path": ["up", "up", "right", ...], "distance": 5}}

You can use this Python template:
```python
import heapq

def manhattan_distance(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)

def astar_pathfind(start_x, start_y, goal_x, goal_y, obstacles):
    # A* implementation here
    # Return list of directions: ["up", "right", "right", ...]
    pass

# Calculate path
path = astar_pathfind({data['player']['x']}, {data['player']['y']},
                      {data['target']['x']}, {data['target']['y']},
                      obstacles=[])
print(path)
```
"""

    return prompt


def create_detailed_map_state(pyboy, radius=5):
    """
    Create comprehensive map state combining table view and pathfinding data.
    This is what gets sent to the LLM.
    """
    # Get basic info
    player_x = pyboy.memory[0xDCB8]
    player_y = pyboy.memory[0xDCB7]

    # Get direction
    direction_byte = pyboy.memory[0xDCBB]
    directions = {
        0x00: "DOWN ↓", 0x04: "UP ↑", 0x08: "LEFT ←", 0x0C: "RIGHT →",
        0x01: "DOWN ↓", 0x05: "UP ↑", 0x09: "LEFT ←", 0x0D: "RIGHT →"  # Movement variants
    }
    facing = directions.get(direction_byte, f"UNKNOWN (0x{direction_byte:02X})")

    # Get collision
    collision = {
        'down': pyboy.memory[0xC2FA] == 0x00,
        'up': pyboy.memory[0xC2FB] == 0x00,
        'left': pyboy.memory[0xC2FC] == 0x00,
        'right': pyboy.memory[0xC2FD] == 0x00
    }

    # Get warps
    warps = get_warp_positions(pyboy)

    # Build complete state
    state = []

    # Add map table
    state.append(create_map_table(pyboy, radius))
    state.append("")

    # Add movement info
    state.append("## Movement Information")
    state.append(f"**Facing:** {facing}")
    state.append("")
    state.append("**Can Move:**")
    for direction, walkable in collision.items():
        status = "✅ Yes" if walkable else "❌ No"
        state.append(f"- {direction.upper()}: {status}")
    state.append("")

    # Add exits info
    if warps:
        state.append("## Exits/Doors")
        for wx, wy in warps:
            distance = abs(wx - player_x) + abs(wy - player_y)

            # Calculate direction
            directions_to_exit = []
            if wy < player_y:
                directions_to_exit.append("north")
            elif wy > player_y:
                directions_to_exit.append("south")
            if wx < player_x:
                directions_to_exit.append("west")
            elif wx > player_x:
                directions_to_exit.append("east")

            direction_str = " and ".join(directions_to_exit) if directions_to_exit else "at your location"

            state.append(f"- Exit at ({wx}, {wy}) - {distance} tiles away, go {direction_str}")

    return "\n".join(state)
