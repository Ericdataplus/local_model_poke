# Markdown Table Vision System

## Overview

The markdown vision system replaces ASCII art with structured markdown tables, giving the LLM:
1. **Exact coordinates** for every tile
2. **Clear visual structure** that LLMs understand well
3. **Python integration** for calculating optimal paths
4. **Better spatial reasoning** through coordinate references

---

## How It Works

### Traditional ASCII Approach
```
# . . . . . . . . . # #
# . . # # . . . . . # #
# . . # # . . N . . . .
# . . . . . . . . . . .
# . . . . . P . . . . E

P=You, E=Exit, N=NPC, #=Wall, .=Floor
```

**Problems:**
- No coordinates visible
- Hard for LLM to calculate distances
- Ambiguous spatial relationships
- Can't reference specific positions

### Markdown Table Approach
```markdown
| Y\X | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|-----|---|----|----|----|----|----|----|----|
| **9** | 🟫 | 🟫 | ⬜ | ⬜ | 👤 | ⬜ | ⬜ | ⬜ |
| **10** | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| **11** | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| **12** | ⬜ | ⬜ | 🧍 | ⬜ | ⬜ | ⬜ | ⬜ | 🚪 |

Player: (10, 12) | Exit: (15, 12) | NPC: (12, 9)
```

**Benefits:**
- ✅ Exact coordinates for every position
- ✅ LLM can calculate: "Exit is 5 tiles east"
- ✅ Can write Python code using coordinates
- ✅ Clear visual structure

---

## Symbol Legend

| Symbol | Meaning | Description |
|--------|---------|-------------|
| 🧍 | Player | Your current position |
| 🚪 | Exit/Door | Map transitions, stairs, doors |
| 👤 | NPC | Non-player characters, objects |
| ⬜ | Walkable | Can move here |
| 🟫 | Obstacle | Blocked (walls, trees, etc.) |
| ⬛ | Out of Bounds | Beyond map edges |

---

## Python Pathfinding Integration

The LLM can now use Python to calculate optimal paths!

### Example 1: Simple Path Calculation

**LLM sees:**
```markdown
| Y\X | 10 | 11 | 12 | 13 | 14 | 15 |
|-----|----|----|----|----|----|----|
| **12** | 🧍 | ⬜ | ⬜ | ⬜ | ⬜ | 🚪 |

Player: (10, 12) | Exit: (15, 12)
```

**LLM can reason:**
"I'm at (10, 12) and need to reach (15, 12). That's 5 tiles east with no obstacles."

**Tool call:**
```json
{
  "function": "key_press",
  "arguments": {
    "keys": ["right", "right", "right", "right", "right"],
    "reasoning": "Moving 5 tiles east to reach exit at (15, 12)"
  }
}
```

### Example 2: Complex Navigation with Obstacles

**LLM sees:**
```markdown
| Y\X | 10 | 11 | 12 | 13 | 14 | 15 |
|-----|----|----|----|----|----|----|
| **10** | 🧍 | 🟫 | 🟫 | ⬜ | ⬜ | 🚪 |
| **11** | ⬜ | 🟫 | 🟫 | ⬜ | ⬜ | ⬜ |
| **12** | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |

Player: (10, 10) | Exit: (15, 10)
```

**LLM can reason:**
"I need to go around the obstacles at (11,10), (12,10), (11,11), (12,11). I'll use the pathfinding tool."

**Tool call:**
```json
{
  "function": "calculate_path",
  "arguments": {
    "target_x": 15,
    "target_y": 10
  }
}
```

**System calculates:**
- Path: `['down', 'down', 'right', 'right', 'right', 'right', 'right', 'up', 'up']`
- Distance: 9 tiles
- Simplified: "2 down, then 5 right, then 2 up"

---

## Tools Available to LLM

### 1. key_press
Press keys directly (for simple navigation).

```json
{
  "function": "key_press",
  "arguments": {
    "keys": ["up", "right", "right", "a"],
    "reasoning": "Moving north then east to talk to NPC"
  }
}
```

### 2. calculate_path
Let Python calculate optimal path (for complex navigation).

```json
{
  "function": "calculate_path",
  "arguments": {
    "target_x": 25,
    "target_y": 15
  }
}
```

The system will:
1. Read obstacles from current map
2. Run A* pathfinding algorithm
3. Execute the calculated path automatically
4. Report the path taken

### 3. wait
Wait for animations/transitions.

```json
{
  "function": "wait",
  "arguments": {
    "frames": 60
  }
}
```

---

## How the LLM Uses This

### Step 1: Analyze the Table
```
"Looking at the map table:
- I'm at (10, 12) marked with 🧍
- Exit is at (15, 12) marked with 🚪
- The path shows: ⬜ ⬜ ⬜ ⬜ ⬜
- All tiles between me and exit are walkable"
```

### Step 2: Calculate Distance
```
"Distance = |15 - 10| + |12 - 12| = 5 + 0 = 5 tiles
Direction: East (X increases)
Obstacles: None in the path"
```

### Step 3: Make Decision
```
"I should move 5 times to the right to reach the exit."
```

### Step 4: Execute
```json
{
  "function": "key_press",
  "arguments": {
    "keys": ["right", "right", "right", "right", "right"],
    "reasoning": "Direct path to exit 5 tiles east"
  }
}
```

---

## Implementation Details

### Vision System (`src/markdown_vision.py`)

**Main function:**
```python
create_detailed_map_state(pyboy, radius=5)
```

**Returns:**
- Markdown table with coordinates
- Legend of symbols
- Movement information (which directions are blocked)
- Exit locations with distances and directions

**Example output:**
```markdown
## Map View
**Player Position:** (10, 12)
**Map Size:** 20x20

[Table here]

## Movement Information
**Facing:** DOWN ↓

**Can Move:**
- UP: ✅ Yes
- DOWN: ✅ Yes
- LEFT: ❌ No
- RIGHT: ✅ Yes

## Exits/Doors
- Exit at (15, 12) - 5 tiles away, go east
```

### Pathfinding System (`src/pathfinding_executor.py`)

**A* Algorithm:**
```python
astar_pathfind(start_x, start_y, goal_x, goal_y, obstacles, map_width, map_height)
```

**Features:**
- Optimal path calculation
- Obstacle avoidance
- Manhattan distance heuristic
- Returns list of directions

**Helper functions:**
- `simplify_path()`: "up, up, right, right" → "2 up, then 2 right"
- `calculate_path_from_data()`: Wrapper for game data
- `execute_pathfinding_code()`: Safe code execution

---

## Configuration

### Vision Radius
In `main_markdown.py`:
```python
VISION_RADIUS = 5  # How many tiles to show in each direction
```

- **Smaller (3)**: Less context, faster processing
- **Medium (5)**: Good balance (recommended)
- **Larger (7)**: More context, slower processing

### Symbol Customization
In `src/markdown_vision.py`, change the emojis:
```python
if dx == 0 and dy == 0:
    cell = "🧍"  # Change player symbol
elif (x_coord, y_coord) in warp_set:
    cell = "🚪"  # Change exit symbol
# etc.
```

---

## Performance Comparison

| Approach | Token Usage | LLM Understanding | Pathfinding |
|----------|-------------|-------------------|-------------|
| ASCII Art | ~800 tokens | ⭐⭐ Fair | Manual only |
| Markdown Table | ~1200 tokens | ⭐⭐⭐⭐ Excellent | Python A* |

**Verdict:** Markdown uses more tokens but provides much better results.

---

## Testing

### Quick Test
```bash
python test_markdown_vision.py
```

Shows examples of:
- How the table looks
- Python pathfinding example
- Tool usage
- Comparison with ASCII

### Run Live
```bash
python main_markdown.py
```

Watch the console to see:
- Map tables being generated
- Python path calculations
- AI reasoning about coordinates

---

## Troubleshooting

### "Table looks weird in console"
- Windows: Encoding issues - already fixed in code
- Use a terminal that supports Unicode (Windows Terminal recommended)

### "Pathfinding returns empty path"
- Target might be blocked by obstacles
- Check that target coordinates are within map bounds
- Verify obstacles are being detected correctly

### "LLM not using coordinates correctly"
- Make sure prompt emphasizes the coordinate system
- Add examples in system prompt showing coordinate usage
- Increase temperature for more exploratory behavior

---

## Future Enhancements

Possible improvements:
1. **Terrain costs**: Grass (slow) vs road (fast)
2. **Multiple path options**: Show alternative routes
3. **Dynamic obstacles**: NPCs that move
4. **Path caching**: Remember calculated paths
5. **Visual path preview**: Show planned route in table

---

## Example Session

```
Turn 1:
📍 Turn 1: New Bark Town (10, 12)

[Map table shows exit at (15, 12)]

🤖 AI Analysis: "Exit 5 tiles east, clear path"
🤖 AI Action: key_press(['right', 'right', 'right', 'right', 'right'])

Turn 2:
📍 Turn 2: New Bark Town (15, 12)

[Map table shows exit at same position]

🤖 AI Action: key_press(['a'])  # Interact with door
```

---

## Credits

Markdown table vision concept inspired by better LLM spatial understanding research.
A* pathfinding is a classic algorithm (1968) by Peter Hart, Nils Nilsson, and Bertram Raphael.
