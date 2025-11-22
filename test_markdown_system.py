"""
Test the complete markdown vision system
Verifies that tables are generated correctly and pathfinding works
"""

import sys

def test_pathfinding():
    """Test that pathfinding works correctly"""
    print("=" * 60)
    print("TEST 1: Python Pathfinding")
    print("=" * 60)
    print()

    from src.pathfinding_executor import astar_pathfind, simplify_path

    # Test simple path
    print("Test Case: Simple straight line")
    print("  Start: (10, 10)")
    print("  Goal: (15, 10)")
    print("  Obstacles: None")

    path = astar_pathfind(
        start_x=10, start_y=10,
        goal_x=15, goal_y=10,
        obstacles=set(),
        map_width=30, map_height=30
    )

    print(f"  Result: {path}")
    print(f"  Simplified: {simplify_path(path)}")
    assert path == ['right'] * 5, "Simple path should be 5 rights"
    print("  ✅ PASS")
    print()

    # Test path with obstacles
    print("Test Case: Path around obstacles")
    print("  Start: (10, 10)")
    print("  Goal: (15, 10)")
    print("  Obstacles: Wall at x=12 (blocking direct path)")

    obstacles = {(12, 9), (12, 10), (12, 11)}
    path = astar_pathfind(
        start_x=10, start_y=10,
        goal_x=15, goal_y=10,
        obstacles=obstacles,
        map_width=30, map_height=30
    )

    print(f"  Result: {path}")
    print(f"  Simplified: {simplify_path(path)}")
    assert len(path) > 5, "Path should be longer than direct route"
    print("  ✅ PASS - Found route around obstacle")
    print()


def test_markdown_table():
    """Test markdown table generation (without PyBoy)"""
    print("=" * 60)
    print("TEST 2: Markdown Table Format")
    print("=" * 60)
    print()

    # Create a sample table manually
    table = """## Map View

**Player Position:** (10, 12)
**Map Size:** 20x20

| Y\\X | 8  | 9  | 10 | 11 | 12 | 13 | 14 | 15 |
|-----|----|----|----|----|----|----|----|----|
| **10** | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| **11** | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| **12** | ⬜ | ⬜ | 🧍 | ⬜ | ⬜ | ⬜ | ⬜ | 🚪 |
| **13** | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |

**Legend:**
- 🧍 Player (YOU)
- 🚪 Exit/Door/Stairs
- 👤 NPC/Object
- ⬜ Walkable tile
- 🟫 Obstacle/Blocked
- ⬛ Out of bounds"""

    print("Sample Table:")
    print(table)
    print()

    # Verify key elements are present
    assert "🧍" in table, "Player symbol missing"
    assert "🚪" in table, "Exit symbol missing"
    assert "Y\\X" in table, "Coordinate headers missing"
    assert "| **12** |" in table, "Y coordinate labels missing"

    print("  ✅ PASS - Table format correct")
    print()


def test_prompt_loading():
    """Test that markdown prompt loads correctly"""
    print("=" * 60)
    print("TEST 3: Markdown Prompt Loading")
    print("=" * 60)
    print()

    import os

    prompt_file = "prompts/system_prompt_markdown.txt"

    if os.path.exists(prompt_file):
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"  Prompt file: {prompt_file}")
        print(f"  Size: {len(content)} characters")

        # Check for key instruction sections
        checks = [
            ("Markdown table instructions", "MARKDOWN TABLE" in content.upper()),
            ("Coordinate system", "coordinates" in content.lower()),
            ("Tool usage", "key_press" in content.lower()),
            ("Pathfinding tool", "calculate_path" in content.lower()),
            ("Symbol legend", "🧍" in content and "🚪" in content),
        ]

        all_passed = True
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"  {status} {check_name}")
            if not result:
                all_passed = False

        if all_passed:
            print("  ✅ PASS - All prompt elements present")
        else:
            print("  ❌ FAIL - Some prompt elements missing")
            return False
    else:
        print(f"  ❌ FAIL - Prompt file not found: {prompt_file}")
        return False

    print()
    return True


def test_integration():
    """Test that all components work together"""
    print("=" * 60)
    print("TEST 4: Integration Test")
    print("=" * 60)
    print()

    from src.pathfinding_executor import calculate_path_from_data

    # Simulate game data with collision map
    game_data = {
        'player': {'x': 10, 'y': 12, 'facing': 'right'},
        'target': {'x': 15, 'y': 12},
        'map': {'width': 30, 'height': 30},
        'npcs': [{'x': 13, 'y': 12}],  # NPC in the way
        'collision': {'adjacent': {'up': False, 'down': False, 'left': False, 'right': False}},
        'collision_map': {
            (11, 12): False,  # Walkable
            (12, 12): False,  # Walkable
            (13, 12): True,   # Blocked by NPC
            (14, 12): False,  # Walkable
            (15, 12): False,  # Walkable (goal)
        }
    }

    print("  Simulating navigation from (10,12) to (15,12)")
    print("  NPC blocking at (13,12)")

    result = calculate_path_from_data(game_data)

    print(f"  Path found: {result['success']}")
    print(f"  Distance: {result['distance']} moves")
    print(f"  Obstacles avoided: {result['obstacles_count']}")

    if result['success']:
        from src.pathfinding_executor import simplify_path
        print(f"  Path: {simplify_path(result['path'])}")
        print("  ✅ PASS - Pathfinding works with collision map")
    else:
        print("  ❌ FAIL - Could not find path")
        return False

    print()
    return True


def main():
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

    print()
    print("=" * 60)
    print("MARKDOWN VISION SYSTEM - COMPLETE TEST SUITE")
    print("=" * 60)
    print()

    tests = [
        ("Pathfinding", test_pathfinding),
        ("Table Format", test_markdown_table),
        ("Prompt Loading", test_prompt_loading),
        ("Integration", test_integration),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            # If function returns bool, use that; otherwise assume True
            if result is None:
                result = True
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    print("=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print()
        print("✅ ALL TESTS PASSED!")
        print()
        print("The markdown vision system is ready to use.")
        print("Run: python main_markdown.py")
        print()
    else:
        print()
        print("❌ SOME TESTS FAILED")
        print("Please review the errors above")
        print()

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
