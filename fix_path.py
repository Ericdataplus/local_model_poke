import re

# Read the file
with open('gui_main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the path execution code
old_code = """                # Execute the path
                for direction in result['path']:
                    if direction == "up": self.pyboy.button('up')
                    elif direction == "down": self.pyboy.button('down')
                    elif direction == "left": self.pyboy.button('left')
                    elif direction == "right": self.pyboy.button('right')
                    self.pyboy.tick()
                    for _ in range(8): self.pyboy.tick()  # Small delay between moves"""

new_code = """                # Execute the path
                for direction in result['path']:
                    # Press button
                    if direction == "up": self.pyboy.button_press('up')
                    elif direction == "down": self.pyboy.button_press('down')
                    elif direction == "left": self.pyboy.button_press('left')
                    elif direction == "right": self.pyboy.button_press('right')
                    
                    # Hold for 8 frames
                    for _ in range(8): self.pyboy.tick()
                    
                    # Release button
                    if direction == "up": self.pyboy.button_release('up')
                    elif direction == "down": self.pyboy.button_release('down')
                    elif direction == "left": self.pyboy.button_release('left')
                    elif direction == "right": self.pyboy.button_release('right')
                    
                    # Wait before next move
                    for _ in range(10): self.pyboy.tick()"""

# Replace
if old_code in content:
    content = content.replace(old_code, new_code)
    print("✓ Replacement successful!")
else:
    print("✗ Old code not found - file may have changed")
    
# Write back
with open('gui_main.py', 'w', encoding='utf-8') as f:
    f.write(content)
    
print("Done!")
