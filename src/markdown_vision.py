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
    # Get player position
    player_x = pyboy.memory[0xDCB8]
    player_y = pyboy.memory[0xDCB7]
    map_width = pyboy.memory[0xD4B1]
    map_height = pyboy.memory[0xD4B2]

    # Get player facing direction
    direction_byte = pyboy.memory[0xDCBB]
    direction_arrows = {
        0x00: "↓",  # DOWN
        0x04: "↑",  # UP
        0x08: "←",  # LEFT
        0x0C: "→"   # RIGHT
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
            elif collision_map.get((x_coord, y_coord), True):
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
    table.append("- ⬜ Walkable - You can move here")
    table.append("- 🟫 Obstacle - BLOCKED (walls, furniture, etc.)")
    table.append("- ⬛ Out of bounds - Beyond map edge")

    return "\n".join(table)


def get_warp_positions(pyboy):
    """Get all warp/exit positions on current map."""
    warps = []
    warp_count = pyboy.memory[0xD4B6]

    for i in range(min(warp_count, 16)):
        base = 0xD4B7 + (i * 5)
        y = pyboy.memory[base]
        x = pyboy.memory[base + 1]
        warps.append((x, y))

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
    Returns dict: {(x, y): is_blocked}

    Uses actual map block collision data from RAM.
    """
    collision_map = {}

    # Get current collision data for adjacent tiles (MOST ACCURATE)
    current_collision = {
        'down': pyboy.memory[0xC2FA],
        'up': pyboy.memory[0xC2FB],
        'left': pyboy.memory[0xC2FC],
        'right': pyboy.memory[0xC2FD]
    }

    # Mark adjacent tiles based on REAL collision data
    if current_collision['up'] == 0x00:
        collision_map[(center_x, center_y - 1)] = False  # Walkable
    else:
        collision_map[(center_x, center_y - 1)] = True   # Blocked

    if current_collision['down'] == 0x00:
        collision_map[(center_x, center_y + 1)] = False
    else:
        collision_map[(center_x, center_y + 1)] = True

    if current_collision['left'] == 0x00:
        collision_map[(center_x - 1, center_y)] = False
    else:
        collision_map[(center_x - 1, center_y)] = True

    if current_collision['right'] == 0x00:
        collision_map[(center_x + 1, center_y)] = False
    else:
        collision_map[(center_x + 1, center_y)] = True

    # For non-adjacent tiles, read map block data
    # Map blocks stored at 0xC800, collision depends on block type
    try:
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

                # Read map block ID
                block_index = y * map_width + x
                if block_index < 1300:  # Max size of map block array
                    block_id = pyboy.memory[0xC800 + block_index]

                    # Simple heuristic: blocks 0-63 are typically walkable
                    # This is a simplification - real collision is more complex
                    # But adjacent tiles (above) have REAL collision data
                    is_blocked = block_id >= 64
                    collision_map[(x, y)] = is_blocked
                else:
                    collision_map[(x, y)] = True  # Unknown = blocked for safety

    except Exception as e:
        # If map block reading fails, mark unknowns as walkable
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                x = center_x + dx
                y = center_y + dy
                if (x, y) not in collision_map:
                    collision_map[(x, y)] = False  # Assume walkable

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
    directions = {0x00: "DOWN ↓", 0x04: "UP ↑", 0x08: "LEFT ←", 0x0C: "RIGHT →"}
    facing = directions.get(direction_byte, "UNKNOWN")

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
