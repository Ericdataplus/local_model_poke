"""Quick script to debug memory addresses for warps"""
import os
from pyboy import PyBoy

ROM_PATH = "roms/crystal.gbc"
SAVE_STATE = "init.state"

pyboy = PyBoy(ROM_PATH, window="null")
pyboy.set_emulation_speed(0)

if os.path.exists(SAVE_STATE):
    with open(SAVE_STATE, "rb") as f:
        pyboy.load_state(f)

# Run a few frames
for _ in range(60):
    pyboy.tick()

# Read player position
player_x = pyboy.memory[0xDCB8]
player_y = pyboy.memory[0xDCB7]
map_group = pyboy.memory[0xDCB5]
map_number = pyboy.memory[0xDCB6]

print(f"Player at ({player_x}, {player_y})")
print(f"Map: Group {map_group}, Number {map_number}")
print()

# Check warp count
warp_count = pyboy.memory[0xD4B6]
print(f"Warp count at 0xD4B6: {warp_count}")
print()

# Read warp data
if warp_count > 0:
    print("Warp data:")
    for i in range(min(warp_count, 16)):
        base = 0xD4B7 + (i * 5)
        y = pyboy.memory[base]
        x = pyboy.memory[base + 1]
        warp_to = pyboy.memory[base + 2]
        map_dest = pyboy.memory[base + 3]
        bank = pyboy.memory[base + 4]
        print(f"  Warp {i}: ({x}, {y}) -> warp {warp_to}, map {map_dest}, bank {bank}")
else:
    print("No warps found!")
    print()
    print("Checking alternate addresses...")
    # Try different possible addresses
    for addr in [0xD4B6, 0xD4B7, 0xD4B8, 0xD4B9, 0xD4BA]:
        val = pyboy.memory[addr]
        print(f"  0x{addr:04X}: {val}")

print()
print("Map dimensions:")
width = pyboy.memory[0xD4B1]
height = pyboy.memory[0xD4B2]
print(f"  Width: {width}, Height: {height}")

print()
print("Object count:")
num_objects = pyboy.memory[0xD4CE]
print(f"  Objects at 0xD4CE: {num_objects}")

if num_objects > 0:
    print("  Object data:")
    for i in range(min(num_objects, 5)):
        base = 0xD4CF + (i * 16)
        sprite_id = pyboy.memory[base]
        y = pyboy.memory[base + 1]
        x = pyboy.memory[base + 2]
        print(f"    Object {i}: sprite {sprite_id} at ({x}, {y})")

pyboy.stop()
