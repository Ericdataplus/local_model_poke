# Direction Byte Debug

## The Problem

The arrow is showing as 🧍 instead of ↑↓←→, and facing shows as "UNKNOWN".

This means the direction byte at memory address **0xDCBB** is not matching the expected values.

## Expected Values

```python
0x00 = DOWN ↓
0x04 = UP ↑
0x08 = LEFT ←
0x0C = RIGHT →
```

## What's Happening

In the run log:
- Line 18: Player shown as **↓** (DOWN arrow) - WORKING!
- Line 68: Player shown as **🧍** - NOT WORKING!
- Line 84: Facing: **UNKNOWN** - direction_byte doesn't match expected values

## Root Cause

The direction byte value is likely changing to something unexpected, OR the memory address 0xDCBB might not be the correct address for Pokemon Crystal (could be different from Pokemon Red/Blue).

## Solution Options

### Option 1: Add Debug Logging

Modify `create_map_table()` to print the actual direction_byte value:

```python
direction_byte = pyboy.memory[0xDCBB]
print(f"[DEBUG] Direction byte: 0x{direction_byte:02X}")
```

This will show us what value is actually being read.

### Option 2: Expand the Direction Map

Pokemon Crystal might use different values. Try adding more possibilities:

```python
direction_arrows = {
    0x00: "↓",  # DOWN
    0x01: "↓",  # DOWN (alternate)
    0x04: "↑",  # UP
    0x05: "↑",  # UP (alternate)
    0x08: "←",  # LEFT
    0x09: "←",  # LEFT (alternate)
    0x0C: "→",  # RIGHT
    0x0D: "→",  # RIGHT (alternate)
}
```

### Option 3: Check Different Memory Address

Pokemon Crystal might store direction at a different address. Common addresses:
- 0xDCBB (what we're using)
- 0xC109 (alternate)
- 0xC2F7 (movement direction)

### Option 4: Use Movement Direction Instead

Instead of facing direction, use the LAST movement direction, which is more reliable:

```python
# Use collision data to infer direction
last_move_byte = pyboy.memory[0xC2F7]
```

## Quick Fix

Add fallback logic that always shows SOMETHING useful:

```python
player_arrow = direction_arrows.get(direction_byte, f"?{direction_byte:02X}")
```

This would show "?4C" if byte is 0x4C, helping us debug what value it actually is.
