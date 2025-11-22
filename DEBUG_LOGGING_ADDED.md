# Debug Logging Added - Ready to Diagnose Issues

## Changes Made

I've added debug logging to `src/markdown_vision.py` to diagnose the two main problems:

### 1. Warp Detection Debug (Lines 117-127)

```python
def get_warp_positions(pyboy):
    warps = []
    warp_count = pyboy.memory[0xD4B6]

    # DEBUG: Print warp detection info
    print(f"[DEBUG] Warp count at 0xD4B6: {warp_count}")

    for i in range(min(warp_count, 16)):
        base = 0xD4B7 + (i * 5)
        y = pyboy.memory[base]
        x = pyboy.memory[base + 1]
        print(f"[DEBUG] Warp {i}: x={x}, y={y} (from base 0x{base:04X})")
        warps.append((x, y))

    print(f"[DEBUG] Total warps found: {len(warps)}")
    return warps
```

**What this shows:**
- How many warps the game thinks exist
- The X,Y coordinates of each warp
- Whether warps are being detected at all

### 2. Direction Byte Debug (Lines 26-28)

```python
# DEBUG: Show actual direction byte if unmapped
if direction_byte not in [0x00, 0x01, 0x04, 0x05, 0x08, 0x09, 0x0C, 0x0D]:
    print(f"[DEBUG] Unknown direction byte: 0x{direction_byte:02X}")
```

**What this shows:**
- If Pokemon Crystal uses direction values we haven't mapped yet
- The actual hex value when direction shows as 🧍

### 3. Collision Detection Debug (Line 173)

```python
# DEBUG: Print collision values
print(f"[DEBUG] Collision at ({center_x}, {center_y}): down=0x{current_collision['down']:02X}, up=0x{current_collision['up']:02X}, left=0x{current_collision['left']:02X}, right=0x{current_collision['right']:02X}")
```

**What this shows:**
- The actual collision byte values at each position
- Whether 0x00 (walkable) or other values (blocked) are being read
- If the memory addresses 0xC2FA-0xC2FD are correct for Pokemon Crystal

## What to Look For

### Next time you run the game, check the console output for:

**1. Warp Detection:**
```
[DEBUG] Warp count at 0xD4B6: 0    ← If this is 0, warps not being detected!
[DEBUG] Total warps found: 0
```

**Expected for Player's House 2F:**
```
[DEBUG] Warp count at 0xD4B6: 1
[DEBUG] Warp 0: x=7, y=0 (from base 0xD4B7)    ← Stairs location
[DEBUG] Total warps found: 1
```

**2. Collision Detection:**
```
[DEBUG] Collision at (3, 4): down=0x00, up=0xFF, left=0xFF, right=0x04
```

This tells us:
- `down=0x00` means walkable below
- `up=0xFF` means blocked above
- If values are all 0x00 but movement still fails, the addresses are wrong

**3. Direction Issues:**
```
[DEBUG] Unknown direction byte: 0x2C    ← New value we need to map!
```

## What the Debug Output Will Tell Us

### If warp_count = 0:
**Problem:** Memory address 0xD4B6 is wrong for Pokemon Crystal
**Solution:** Try alternate addresses:
- 0xD490 (alternate warp count)
- 0xCF0C (map connection data)

### If collision values don't match actual movement:
**Problem:** Addresses 0xC2FA-0xC2FD are wrong
**Solution:** Try alternate addresses:
- 0xC2E8-0xC2EB (alternate collision)
- Use only visual block detection, ignore collision bytes

### If direction byte shows unknown values:
**Problem:** Pokemon Crystal uses different direction encoding
**Solution:** Map the new values based on what we see

## Quick Test

Run the game now and watch the console. You should see lines like:
```
[DEBUG] Warp count at 0xD4B6: ?
[DEBUG] Collision at (3, 3): down=0x??, up=0x??, left=0x??, right=0x??
```

Copy those debug lines and send them to me - I'll immediately know what's wrong and how to fix it!

## Summary of What's Fixed So Far

✅ **Arrows showing** - Direction arrows (↑↓←→) now display correctly
✅ **Debug logging added** - Will show exactly what's being read from memory
⏳ **Warps not showing** - Debug will reveal why (waiting for log output)
⏳ **Collision wrong** - Debug will show actual vs expected values (waiting for log output)

Once you run the game and see the debug output, we'll know exactly what memory addresses are wrong and can fix them immediately!
