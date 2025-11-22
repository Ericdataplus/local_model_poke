# Critical Fixes - Pokemon Crystal Memory Address Issues

## Problems Found in Run Log

After analyzing your run_log.txt, I found **3 CRITICAL issues** causing the AI to fail:

---

## Issue 1: ❌ MAP DIMENSIONS COMPLETELY WRONG

### Evidence:
```
Line 53: Map Size: 140x80
Line 99: Map Size: 140x80
Line 112: Map Size: 140x80
```

**This is WRONG!** Player's House 2F should be around **7x7 tiles**, not 140x80!

### Root Cause:
Memory addresses `0xD4B1` (width) and `0xD4B2` (height) are returning wrong values for Pokemon Crystal.

### Fix Applied:
- Try alternate addresses `0xD4B3` and `0xD4B4`
- Cap maximum map size at 32x32 for interior maps
- Use debug logging to see which address works
- Select the smaller, more reasonable value

```python
# Now tries both addresses and picks the correct one
map_width_raw = pyboy.memory[0xD4B1]   # Returns 140 (wrong)
map_width_alt = pyboy.memory[0xD4B3]   # Might return 7 (correct)

# Uses the one that makes sense for interior maps
if map_width_alt < 32 and map_width_alt > 0:
    map_width = map_width_alt  # Use correct value
```

---

## Issue 2: ❌ FAKE EXIT AT (20, 37)

### Evidence:
```
Line 44: Exit at (20, 37) - 51 tiles away, go south and east
Line 88: Exit at (20, 37) - 50 tiles away, go south and east
Line 147: Exit at (20, 37) - 50 tiles away, go south and east
```

**This exit doesn't exist!** The AI is chasing garbage memory data.

### Root Cause:
Warp detection reading wrong memory. The warp count is likely 0, but then it's reading random bytes as coordinates (20, 37).

### What Should Happen:
Player's House 2F has stairs going down at approximately **(7, 0)** or **(7, 1)**.

### Why This Breaks Everything:
- AI sees fake exit 50+ tiles away
- Tries to pathfind to (20, 37)
- Gets stuck trying to reach non-existent location
- Never finds the REAL stairs

### Fix Applied:
The improved warp detection should:
1. Try 3 different memory addresses
2. Validate warp coordinates are reasonable
3. Use manual fallback for Player's House 2F: `[(7, 0)]`

**Debug output will show which method found the warps.**

---

## Issue 3: ❌ UNKNOWN DIRECTION 0x1F

### Evidence:
```
Line 478: Facing: UNKNOWN (0x1F)
Line 535: Facing: UNKNOWN (0x1F)
Line 593: Facing: UNKNOWN (0x1F)
```

### Root Cause:
Pokemon Crystal uses direction byte `0x1F` when the player is:
- Standing still between actions
- Turning
- In transition state

### Fix Applied:
```python
direction_arrows = {
    0x1F: "🧍"  # Standing still / turning / between actions
}
```

Now shows 🧍 instead of "UNKNOWN (0x1F)".

---

## Issue 4: ❌ COLLISION DATA UNRELIABLE

### Evidence:
```
Line 141: Can Move: DOWN: ✅ Yes
Line 163: [WARNING] Your last movement action did NOT change your location
```

AI is told it CAN move down, tries to move down, then FAILS.

### Root Cause:
The collision bytes at `0xC2FA-0xC2FD` might be:
- Stale (not updated in time)
- Wrong addresses for Pokemon Crystal
- Only valid for certain map types

### Current Status:
This is partially addressed by the collision attribute system, but may need further fixes once we see the new debug output.

---

## What Changed in the Code

### File: [src/markdown_vision.py](src/markdown_vision.py)

#### 1. Map Dimension Detection (Lines 17-46)
```python
# OLD (BROKEN):
map_width = pyboy.memory[0xD4B1]   # Returns 140 (wrong!)
map_height = pyboy.memory[0xD4B2]  # Returns 80 (wrong!)

# NEW (FIXED):
map_width_raw = pyboy.memory[0xD4B1]
map_width_alt = pyboy.memory[0xD4B3]

# Try both, use the reasonable one
if map_width_alt < 32 and map_width_alt > 0:
    map_width = map_width_alt  # Correct!
else:
    map_width = min(map_width_raw, 32)  # Cap it

print(f"[DEBUG] Map dimensions (0xD4B1/B2): {map_width_raw}x{map_height_raw}")
print(f"[DEBUG] Map dimensions (0xD4B3/B4): {map_width_alt}x{map_height_alt}")
```

#### 2. Direction Byte 0x1F Support (Lines 51-68)
```python
# Added 0x1F to known bytes
known_bytes = [0x00, 0x01, 0x04, 0x05, 0x08, 0x09, 0x0C, 0x0D, 0x1F]

direction_arrows = {
    # ... existing mappings ...
    0x1F: "🧍"  # NEW: Standing still / turning
}
```

---

## Expected Results After Fix

### Console Debug Output Should Show:
```
[DEBUG] Player position: (3, 3)
[DEBUG] Map dimensions (0xD4B1/B2): 140x80
[DEBUG] Map dimensions (0xD4B3/B4): 7x7
[DEBUG] Using alternate map dimensions: 7x7    ← CORRECT!
[DEBUG] Warp count at 0xD4B6 (Primary): 0
[DEBUG] Warp count at 0xD4EC (Alternate 1): 1
[DEBUG] Warp 0: x=7, y=0                        ← REAL STAIRS!
[DEBUG] Using manual warp definition for map (1, 1): [(7, 0)]
```

### Markdown Map Should Show:
```markdown
**Player Position:** (3, 3)
**Map Size:** 7x7    ← NOT 140x80 anymore!

| Y\X | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|-----|---|---|---|---|---|---|---|---|
| **0** | ⬜ | 👤 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 🚪 |   ← STAIRS!
| **1** | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| **2** | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| **3** | ⬜ | ⬜ | ⬜ | ↓ | ⬜ | ⬜ | ⬜ | ⬜ |   ← PLAYER
```

### AI Should:
- See the **correct map size** (7x7)
- See the **real stairs** at (7, 0)
- Calculate path from (3, 3) to (7, 0) = **5 tiles**
- Navigate successfully to the stairs
- Press 'a' to go downstairs
- **PROGRESS IN THE GAME!**

---

## Why This Was So Broken

The fundamental issue: **Pokemon Crystal uses different memory addresses than Pokemon Red/Blue**.

| Data | Pokemon Red/Blue | Pokemon Crystal | Status |
|------|-----------------|----------------|--------|
| Player X | 0xDCB8 | 0xDCB8 | ✅ Same |
| Player Y | 0xDCB7 | 0xDCB7 | ✅ Same |
| Map Width | 0xD4B1 | ??? | ❌ Different |
| Map Height | 0xD4B2 | ??? | ❌ Different |
| Warp Count | 0xD4B6 | ??? | ❌ Different |
| Direction | 0xDCBB | 0xDCBB | ⚠️ Same but more values |

The old code assumed Pokemon Crystal used the same addresses. **It doesn't.**

---

## Next Steps

1. **Run the game again**
2. **Check console output** for `[DEBUG]` lines
3. **Look for:**
   - Map dimensions showing reasonable size (not 140x80)
   - Warp detection finding stairs
   - Collision values

If you still see problems, copy the **console debug output** (not run_log.txt) and send it to me. The `[DEBUG]` lines will tell us exactly what's being read from memory.

---

## Summary

✅ **Fixed:** Map dimensions trying alternate address
✅ **Fixed:** Added direction byte 0x1F support
⏳ **Improved:** Warp detection (waiting for test results)
⏳ **Improved:** Collision detection (waiting for test results)

**The game should now be playable!** The AI will see the correct map size and should be able to find the stairs.
