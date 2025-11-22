"""
Test script to visualize the markdown table vision system.
Shows what the LLM will see when using markdown tables.
"""

import sys


def create_demo_map_table():
    """Create a demo markdown table showing what the AI sees."""

    print("=" * 60)
    print("MARKDOWN TABLE VISION - DEMO")
    print("=" * 60)
    print()
    print("This is what the LLM sees when using markdown table vision:")
    print()

    table = """## Map View

**Player Position:** (10, 12)
**Map Size:** 20x20

| Y\\X | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|-----|---|---|---|---|---|----|----|----|----|----|----|
| **7** | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 🟫 | 🟫 |
| **8** | ⬜ | ⬜ | 🟫 | 🟫 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 🟫 | 🟫 |
| **9** | ⬜ | ⬜ | 🟫 | 🟫 | ⬜ | ⬜ | 👤 | ⬜ | ⬜ | ⬜ | ⬜ |
| **10** | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| **11** | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| **12** | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 🧍 | ⬜ | ⬜ | ⬜ | ⬜ | 🚪 |
| **13** | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| **14** | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| **15** | ⬜ | ⬜ | 🟫 | 🟫 | 🟫 | 🟫 | 🟫 | ⬜ | ⬜ | ⬜ | ⬜ |
| **16** | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| **17** | ⬜ | 🚪 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |

**Legend:**
- 🧍 Player (YOU)
- 🚪 Exit/Door/Stairs
- 👤 NPC/Object
- ⬜ Walkable tile
- 🟫 Obstacle/Blocked
- ⬛ Out of bounds

## Movement Information
**Facing:** DOWN ↓

**Can Move:**
- UP: ✅ Yes
- DOWN: ✅ Yes
- LEFT: ✅ Yes
- RIGHT: ✅ Yes

## Exits/Doors
- Exit at (15, 12) - 5 tiles away, go east
- Exit at (6, 17) - 9 tiles away, go south and west
"""

    print(table)
    print()
    print("=" * 60)
    print("ADVANTAGES OF MARKDOWN TABLE VISION:")
    print("=" * 60)
    print()
    print("✅ Clear coordinate system - LLM can reference exact positions")
    print("✅ Visual structure - Tables are well-understood by LLMs")
    print("✅ No ASCII confusion - Uses clear emoji symbols")
    print("✅ Easy to parse - LLM can extract coordinates programmatically")
    print("✅ Python integration - Can calculate paths using coordinates")
    print()
    print("=" * 60)
    print()


def show_pathfinding_example():
    """Show example of LLM calculating path with Python."""

    print("=" * 60)
    print("PATHFINDING WITH PYTHON - EXAMPLE")
    print("=" * 60)
    print()
    print("The LLM can now write Python code to calculate paths:")
    print()

    code_example = '''```python
# LLM sees the map table and writes:
from pathfinding_executor import astar_pathfind

# Player at (10, 12), want to reach exit at (15, 12)
obstacles = {(7, 8), (8, 8), (7, 9), (8, 9)}  # From table
path = astar_pathfind(
    start_x=10, start_y=12,
    goal_x=15, goal_y=12,
    obstacles=obstacles,
    map_width=20, map_height=20
)

# Result: ['right', 'right', 'right', 'right', 'right']
print(path)
```'''

    print(code_example)
    print()
    print("The AI can:")
    print("1. Read coordinates from the markdown table")
    print("2. Identify obstacles (🟫) and their positions")
    print("3. Write Python code to calculate optimal path")
    print("4. Execute the calculated path")
    print()
    print("=" * 60)
    print()


def show_tool_usage():
    """Show how the AI uses tools with markdown vision."""

    print("=" * 60)
    print("AI TOOL USAGE WITH MARKDOWN VISION")
    print("=" * 60)
    print()

    example = '''
AI Analysis:
"Looking at the map table, I can see:
- I'm at position (10, 12) marked with 🧍
- There's an exit at (15, 12) marked with 🚪
- The path is clear (all ⬜ between me and exit)
- Distance: 5 tiles to the east
- No obstacles in the way"

AI Decision:
"I should move directly east to reach the exit."

Tool Call:
{
  "function": "key_press",
  "arguments": {
    "keys": ["right", "right", "right", "right", "right"],
    "reasoning": "Moving 5 tiles east to reach exit at (15, 12)"
  }
}

OR for complex navigation:

Tool Call:
{
  "function": "calculate_path",
  "arguments": {
    "target_x": 15,
    "target_y": 12
  }
}
'''

    print(example)
    print()
    print("=" * 60)
    print()


def show_comparison():
    """Compare ASCII vs Markdown vision."""

    print("=" * 60)
    print("ASCII vs MARKDOWN - COMPARISON")
    print("=" * 60)
    print()

    print("OLD ASCII APPROACH:")
    print("-" * 40)
    ascii_example = """
# . . . . . . . . . # #
# . . # # . . . . . # #
# . . # # . . N . . . .
# . . . . . . . . . . .
# . . . . . . . . . . .
# . . . . . P . . . . E
# . . . . . . . . . . .

P=You, E=Exit, N=NPC, #=Wall, .=Floor
"""
    print(ascii_example)

    print("\nNEW MARKDOWN APPROACH:")
    print("-" * 40)
    markdown_example = """
| Y\\X | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|-----|---|----|----|----|----|----|----|----|
| **9** | 🟫 | 🟫 | ⬜ | ⬜ | 👤 | ⬜ | ⬜ | ⬜ |
| **10** | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| **11** | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| **12** | ⬜ | ⬜ | 🧍 | ⬜ | ⬜ | ⬜ | ⬜ | 🚪 |

Player: (10, 12) | Exit: (15, 12) | NPC: (12, 9)
"""
    print(markdown_example)

    print("\n✅ Markdown Benefits:")
    print("   - Exact coordinates visible")
    print("   - Clear spatial relationships")
    print("   - Easy to reference in Python code")
    print("   - Better LLM understanding")
    print()
    print("=" * 60)
    print()


def main():
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

    print()
    create_demo_map_table()
    show_pathfinding_example()
    show_tool_usage()
    show_comparison()

    print("=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print()
    print("To use markdown vision with your AI:")
    print()
    print("1. Run: python main_markdown.py")
    print()
    print("This will use the new vision system with:")
    print("   ✅ Markdown tables for spatial understanding")
    print("   ✅ Python A* pathfinding")
    print("   ✅ Coordinate-based navigation")
    print("   ✅ Clear reasoning in tool calls")
    print()
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
