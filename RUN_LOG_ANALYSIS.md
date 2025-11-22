# Run Log Analysis - Issues Found

## Summary of Problems

After checking your run_log.txt, I found **3 critical issues**:

### 1. ✅ PARTIALLY FIXED: Arrow Direction
**Problem:** Player showing as 🧍 instead of arrows
**Cause:** Pokemon Crystal uses more direction byte values than expected
**Fix Applied:** Added movement variant bytes (0x01, 0x05, 0x09, 0x0D) to the direction map

**Status:** Should work better now, but if "UNKNOWN" still shows, it will now display the hex value to help debug

### 2. ❌ CRITICAL: No Exits Showing
**Problem:** The map shows NO 🚪 symbols (exits/stairs/doors)
**Evidence from log:**
```
| Y\X | -2 | -1 | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| **0** | ⬛ | ⬛ | ⬜ | 👤 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| **3** | ⬛ | ⬛ | ⬜ | ⬜ | ⬜ | ↓ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
```
**No 🚪 anywhere!**

**Cause:** Two possibilities:
1. `get_warp_positions()` isn't reading warps correctly from memory
2. Player's House 2F doesn't have warps registered at the expected memory addresses

**What should show:** There MUST be stairs going down - this is Player's House 2F!

### 3. ❌ CRITICAL: AI Getting Stuck on "Walkable" Tiles
**Problem:** Map shows ⬜ (walkable) everywhere, but AI can't move
**Evidence:**
```
Line 519: **Can Move:** RIGHT: ✅ Yes
Line 537: [TOOL] Executing: key_press({'keys': ['right']})
Line 538: [WARNING] Your last movement action did NOT change your location
```

**The AI is told it CAN move right, tries to move right, then FAILS**

**Cause:** The collision detection at memory addresses 0xC2FA-0xC2FD might not be accurate for Player's House 2F

## What's Actually Happening

Looking at the location data:
```
Location: Player's House 2F (24, 7) at (3, 3)
```

The player is in a 7x24 room, but the collision map is showing almost everything as walkable when it's clearly not.

## Root Cause

The issue is that **Player's House 2F is a small room with walls**, but:
1. The warp detection isn't finding the stairs
2. The collision detection is marking invisible walls as walkable
3. The map is using coordinates that go negative (-2, -1) which suggests the coordinate system is off

## The Real Problem

Looking at line 68:
```
| **4** | ⬛ | ⬛ | ⬜ | ⬜ | ⬜ | 🧍 | 🟫 | ⬜ | ⬜ | ⬜ | ⬜ |
```

There IS a 🟫 obstacle showing at (4, 4), but then later that same obstacle disappears!

**The collision map is inconsistent.**

## Immediate Fixes Needed

### Fix 1: Debug Warp Detection
Add logging to see what warps are being detected:

```python
def get_warp_positions(pyboy):
    warps = []
    warp_count = pyboy.memory[0xD4B6]
    print(f"[DEBUG] Warp count: {warp_count}")

    for i in range(min(warp_count, 16)):
        base = 0xD4B7 + (i * 5)
        y = pyboy.memory[base]
        x = pyboy.memory[base + 1]
        print(f"[DEBUG] Warp {i}: ({x}, {y})")
        warps.append((x, y))

    return warps
```

### Fix 2: Improve Collision Detection

The current collision detection uses:
- Adjacent tile collision (0xC2FA-0xC2FD) - ACCURATE but only for 4 tiles
- Map block heuristic (block_id >= 64) - INACCURATE

**Problem:** The heuristic is wrong. Block IDs don't directly correlate to collision in Pokemon Crystal.

**Solution:** Only trust the adjacent tile collision data, mark everything else as unknown:

```python
# For non-adjacent tiles, assume walkable but warn
collision_map[(x, y)] = False  # Assume walkable for distant tiles
```

### Fix 3: Show "Unknown" Tiles Differently

Instead of showing distant tiles as ⬜ (walkable) when we don't know, show them as a different symbol:

```
⬜ = Known walkable (adjacent, collision data confirms)
░░ = Assumed walkable (no collision data, might be wrong)
🟫 = Known blocked (adjacent, collision data confirms)
```

## Quick Test

Can you show me the actual game screen? The Player's House 2F should have:
- A bed
- A PC
- Stairs going down
- 4 walls

The memory reading might be incorrect for this specific map.

## Recommendation

**Try moving to a different map first!** The starter area (outside) has more reliable collision detection. Player's House might have special memory layouts.

To test: Walk outside and see if collision/exits work better there.
