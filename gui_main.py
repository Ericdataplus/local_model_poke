import os
import time
import base64
import io
import threading
import queue
import tkinter as tk
from tkinter import scrolledtext, font
from PIL import Image, ImageTk
from pyboy import PyBoy
from openai import OpenAI
from src.maps import get_map_name
from src.markdown_vision import create_detailed_map_state, create_pathfinding_data
from src.pathfinding_executor import calculate_path_from_data, simplify_path
from src.walkthrough_manager import WalkthroughManager

# Configuration
ROM_PATH = "roms/crystal.gbc"
SAVE_STATE = "init.state"
MODEL_NAME = "local-model"
API_BASE = "http://10.237.108.224:1234/v1"
API_KEY = "lm-studio"

# Load markdown vision system prompt
try:
    with open("prompts/system_prompt_markdown.txt", 'r', encoding='utf-8') as f:
        SYSTEM_PROMPT = f.read()
except:
    # Fallback prompt if file doesn't exist
    SYSTEM_PROMPT = """
# Pokemon Crystal AI - Markdown Vision

You are playing Pokemon Crystal with MARKDOWN TABLE vision.

## CRITICAL: Read the Map Table
You will see coordinates in a markdown table:
| Y\\X | 10 | 11 | 12 |
|-----|----|----|-----|
| **12** | 🧍 | ⬜ | 🚪 |

- 🧍 = You at (10, 12)
- 🚪 = Exit at (12, 12)
- 🟫 = Obstacle (blocked)
- ⬜ = Walkable

## Movement Rules
1. Move ONE direction at a time
2. Do NOT combine directions like ["right", "up"]
3. Use calculate_path for complex navigation

## Available Actions

### key_press
**Movement keys**: "up", "down", "left", "right" - Move in that direction
**Face keys**: "face_up", "face_down", "face_left", "face_right" - Turn without moving
**Interact**: "a" - Interact/confirm, "b" - Cancel/back
**Special**: "a_until_end_of_dialog" - Auto-advance through all dialogue
**Menu**: "start" - Open menu, "select" - Use select

### wait
Wait for animations (frames=60 for 1 second)

### query_walkthrough
Search the walkthrough when stuck

## Game State Info
You receive:
- **Screenshot** of the game
- **Location**: Map name and coordinates (x, y)
- **Facing**: Direction you're pointing (UP ↑, DOWN ↓, LEFT ←, RIGHT →)
- **Grid View**: 9x9 grid showing P=You, N=NPC, E=EXIT, .=Unknown, #=Blocked
- **Collision Data**: Which directions are WALKABLE vs BLOCKED
- **Exit Location**: Coordinates of stairs/doors

## Navigation Strategy

### Step 1: Analyze Situation
- Where am I? (current x,y)
- Where do I need to go? (exit x,y)
- Which direction am I facing?
- What's blocking me? (collision data)

### Step 2: Plan Full Path
Calculate ALL moves needed to reach destination.

Example: At (3,3) facing DOWN, need to reach exit at (7,0):
1. Turn right: face_right
2. Move right 4 times: right, right, right, right  
3. Turn up: face_up
4. Move up 3 times: up, up, up

### Step 3: Execute Complete Sequence
Send ALL keys in ONE action:
```
key_press(keys=["face_right", "right", "right", "right", "right", "face_up", "up", "up", "up"])
```

## Dialogue Handling
When you see text/dialogue:
```
key_press(keys=["a_until_end_of_dialog"])
```

## Common Situations

**Stuck at same position?**
- Check FACING direction - you might have just turned
- Check COLLISION - is that direction actually walkable?
- Try a different walkable direction

**Need to talk to NPC?**
1. Face them: key_press(keys=["face_up"])  (or whatever direction)
2. Interact: key_press(keys=["a"])
3. Advance dialogue: key_press(keys=["a_until_end_of_dialog"])

**Multiple exits?**
Go to the closest one using collision-safe path.

## Remember
- **Plan ahead**: Think through the ENTIRE path before acting
- **Use collision data**: Only move in WALKABLE directions
- **Batch your moves**: Send 5-10 keys per action, not 1
- **Trust the data**: Collision data is 100% accurate from game RAM

Now execute your action!
"""

class PokemonAgent:
    def __init__(self, walkthrough_manager):
        self.client = OpenAI(base_url=API_BASE, api_key=API_KEY)
        self.history = []
        self.walkthrough = walkthrough_manager

    def get_action(self, image_base64, game_state, feedback=""):
        try:
            user_content = [
                {"type": "text", "text": f"GAME STATE:\n{game_state}"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image_base64}"
                    },
                },
            ]
            
            if feedback:
                user_content.insert(0, {"type": "text", "text": f"⚠️ FEEDBACK: {feedback}"})

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ]
            
            if self.history:
                messages.append({"role": "assistant", "content": "Previous actions:\n" + "\n".join(self.history[-25:])})

            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=[{
                    "type": "function",
                    "function": {
                        "name": "key_press",
                        "description": "Press keys on the GameBoy",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "keys": {
                                    "type": "array",
                                    "items": {"type": "string", "enum": ["up", "down", "left", "right", "a", "b", "start", "select", "face_up", "face_down", "face_left", "face_right", "a_until_end_of_dialog"]}
                                }
                            },
                            "required": ["keys"]
                        }
                    }
                }, {
                    "type": "function",
                    "function": {
                        "name": "wait",
                        "description": "Wait for frames",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "frames": {"type": "integer", "default": 60}
                            }
                        }
                    }
                }, {
                    "type": "function",
                    "function": {
                        "name": "query_walkthrough",
                        "description": "Query the walkthrough",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"}
                            },
                            "required": ["query"]
                        }
                    }
                }, {
                    "type": "function",
                    "function": {
                        "name": "calculate_path",
                        "description": "Calculate optimal path to target coordinates using Python A* pathfinding",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "target_x": {"type": "integer", "description": "Target X coordinate from map table"},
                                "target_y": {"type": "integer", "description": "Target Y coordinate from map table"}
                            },
                            "required": ["target_x", "target_y"]
                        }
                    }
                }],
                tool_choice="auto",
                max_tokens=150,
                timeout=120.0
            )
            return response.choices[0].message

        except Exception as e:
            return f"Error: {e}"

def read_memory(pyboy):
    x = pyboy.memory[0xDCB8]
    y = pyboy.memory[0xDCB7]
    map_group = pyboy.memory[0xDCB5]
    map_number = pyboy.memory[0xDCB6]
    party_count = pyboy.memory[0xDCD7]
    
    map_name = get_map_name(map_group, map_number)
    return f"Location: {map_name} ({map_group}, {map_number}) at ({x}, {y})\nParty Count: {party_count}\n", x, y

class PokeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pokemon Crystal AI Inspector")
        self.root.geometry("1000x800")
        
        # Layout
        self.main_frame = tk.Frame(root, bg="#2b2b2b")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left Side: Game Screen
        self.game_frame = tk.Frame(self.main_frame, bg="black", width=480, height=432)
        self.game_frame.pack(side=tk.LEFT, padx=20, pady=20, fill=tk.BOTH)
        self.game_label = tk.Label(self.game_frame, bg="black")
        self.game_label.pack(expand=True)
        
        # Right Side: Logs
        self.log_frame = tk.Frame(self.main_frame, bg="#1e1e1e")
        self.log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(self.log_frame, bg="#1e1e1e", fg="#d4d4d4", font=("Consolas", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.tag_config("user", foreground="#569cd6")
        self.log_text.tag_config("ai", foreground="#ce9178")
        self.log_text.tag_config("tool", foreground="#4ec9b0")
        self.log_text.tag_config("system", foreground="#6a9955")
        self.log_text.tag_config("warning", foreground="#ffcc00")
        
        # Initialize PyBoy
        if not os.path.exists(ROM_PATH):
            self.log("system", f"ROM not found: {ROM_PATH}")
            return

        self.pyboy = PyBoy(ROM_PATH, window="null")
        self.pyboy.set_emulation_speed(0)
        
        if os.path.exists(SAVE_STATE):
            with open(SAVE_STATE, "rb") as f:
                self.pyboy.load_state(f)
                
        self.walkthrough = WalkthroughManager()
        self.agent = PokemonAgent(self.walkthrough)
        self.ai_queue = queue.Queue()
        self.ai_thinking = False
        self.frame_count = 0
        self.last_x = -1
        self.last_y = -1
        self.last_action = ""
        
        # File logging - overwrite on each run
        self.log_file = open("run_log.txt", "w", encoding="utf-8")
        self.log_file.write("=== NEW RUN ===\n")
        self.log_file.flush()
        
        self.log("system", "System initialized. Starting game loop...")
        self.update_loop()
        
    def log(self, tag, message):
        """Log to both GUI, terminal, and file."""
        log_line = f"[{tag.upper()}] {message}"
        self.log_text.insert(tk.END, log_line + "\n", tag)
        self.log_text.see(tk.END)
        # Print to terminal
        print(log_line)
        # Write to file
        self.log_file.write(log_line + "\n")
        self.log_file.flush()

    def execute_action(self, tool_call):
        name = tool_call.function.name
        import json
        args = json.loads(tool_call.function.arguments)
        
        summary = f"{name}({args})"
        self.log("tool", f"Executing: {summary}")
        self.last_action = name # Store action type
        
        if name == "key_press":
            for key in args["keys"]:
                # Special: Face direction without moving (just turn)
                if key == "face_up":
                    self.pyboy.button_press('up')
                    for _ in range(4): self.pyboy.tick()  # Short press to turn
                    self.pyboy.button_release('up')
                    for _ in range(5): self.pyboy.tick()
                    continue
                elif key == "face_down":
                    self.pyboy.button_press('down')
                    for _ in range(4): self.pyboy.tick()
                    self.pyboy.button_release('down')
                    for _ in range(5): self.pyboy.tick()
                    continue
                elif key == "face_left":
                    self.pyboy.button_press('left')
                    for _ in range(4): self.pyboy.tick()
                    self.pyboy.button_release('left')
                    for _ in range(5): self.pyboy.tick()
                    continue
                elif key == "face_right":
                    self.pyboy.button_press('right')
                    for _ in range(4): self.pyboy.tick()
                    self.pyboy.button_release('right')
                    for _ in range(5): self.pyboy.tick()
                    continue
                
                # Special: Press A until dialogue ends
                elif key == "a_until_end_of_dialog":
                    for _ in range(20):  # Press A up to 20 times
                        self.pyboy.button_press('a')
                        for _ in range(4): self.pyboy.tick()
                        self.pyboy.button_release('a')
                        for _ in range(10): self.pyboy.tick()
                    continue
                
                # Regular button press and HOLD
                if key == "up": self.pyboy.button_press('up')
                elif key == "down": self.pyboy.button_press('down')
                elif key == "left": self.pyboy.button_press('left')
                elif key == "right": self.pyboy.button_press('right')
                elif key == "a": self.pyboy.button_press('a')
                elif key == "b": self.pyboy.button_press('b')
                elif key == "start": self.pyboy.button_press('start')
                elif key == "select": self.pyboy.button_press('select')
                
                # Hold button for several frames so game registers it
                for _ in range(8):
                    self.pyboy.tick()
                
                # Release button
                if key == "up": self.pyboy.button_release('up')
                elif key == "down": self.pyboy.button_release('down')
                elif key == "left": self.pyboy.button_release('left')
                elif key == "right": self.pyboy.button_release('right')
                elif key == "a": self.pyboy.button_release('a')
                elif key == "b": self.pyboy.button_release('b')
                elif key == "start": self.pyboy.button_release('start')
                elif key == "select": self.pyboy.button_release('select')
                
                # Wait a bit before next button
                for _ in range(10):
                    self.pyboy.tick()
            
            # Extra wait after all buttons
            for _ in range(10): self.pyboy.tick()
            
        elif name == "wait":
            frames = args.get("frames", 60)
            for _ in range(frames): self.pyboy.tick()
            
        elif name == "query_walkthrough":
            query_text = args.get("query", "")
            result = self.walkthrough.query(query_text)
            self.log("tool", f"Walkthrough result: {result[:200]}...")

        elif name == "calculate_path":
            target_x = args.get("target_x")
            target_y = args.get("target_y")
            self.log("tool", f"Calculating path to ({target_x}, {target_y})...")

            # Get pathfinding data
            data = create_pathfinding_data(self.pyboy, target_x, target_y, radius=10)

            # Calculate path
            result = calculate_path_from_data(data)

            if result['success'] and result['path']:
                path_desc = simplify_path(result['path'])
                self.log("tool", f"Path found: {path_desc} ({result['distance']} tiles)")

                # Execute the path
                for direction in result['path']:
                    if direction == "up": self.pyboy.button('up')
                    elif direction == "down": self.pyboy.button('down')
                    elif direction == "left": self.pyboy.button('left')
                    elif direction == "right": self.pyboy.button('right')
                    self.pyboy.tick()
                    for _ in range(8): self.pyboy.tick()  # Small delay between moves
            else:
                self.log("warning", f"Path calculation failed - no route to ({target_x}, {target_y})")

        return summary
    
    def ai_thread_func(self, img_b64, state_text, feedback):
        response = self.agent.get_action(img_b64, state_text, feedback)
        self.ai_queue.put(response)

    def update_loop(self):
        # Tick PyBoy
        self.pyboy.tick()
        self.frame_count += 1
        
        # Update Screen (every 5 frames to save UI resources)
        if self.frame_count % 5 == 0:
            screen = self.pyboy.screen.image
            # Scale up 3x
            screen = screen.resize((160*3, 144*3), Image.NEAREST)
            img_tk = ImageTk.PhotoImage(screen)
            self.game_label.config(image=img_tk)
            self.game_label.image = img_tk
            
        # Check AI Queue
        try:
            response = self.ai_queue.get_nowait()
            self.ai_thinking = False
            
            if isinstance(response, str) and response.startswith("Error"):
                self.log("system", response)
            else:
                if response.content:
                    self.log("ai", f"Thought: {response.content}")

                if response.tool_calls:
                    # Proper tool calls from API
                    for tool_call in response.tool_calls:
                        summary = self.execute_action(tool_call)
                        self.agent.history.append(summary)
                        if len(self.agent.history) > 50: self.agent.history.pop(0)
                elif response.content:
                    # Fallback: Parse JSON from text (for models without function calling)
                    import json
                    import re
                    content = response.content

                    # Try to extract JSON from markdown code block
                    json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
                    if json_match:
                        try:
                            action_json = json.loads(json_match.group(1))
                            function_name = action_json.get("function")
                            arguments = action_json.get("arguments", {})

                            self.log("tool", f"Parsed fallback action: {function_name}({arguments})")

                            # Create a mock tool call object
                            class MockToolCall:
                                def __init__(self, name, args):
                                    self.function = type('obj', (object,), {
                                        'name': name,
                                        'arguments': json.dumps(args)
                                    })()

                            mock_call = MockToolCall(function_name, arguments)
                            summary = self.execute_action(mock_call)
                            self.agent.history.append(summary)
                            if len(self.agent.history) > 50: self.agent.history.pop(0)

                        except json.JSONDecodeError as e:
                            self.log("warning", f"Failed to parse JSON: {e}")
                            self.log("ai", "No valid action taken.")
                    else:
                        self.log("ai", "No action taken.")
                    
        except queue.Empty:
            pass

        # Trigger AI
        if not self.ai_thinking and self.frame_count % 60 == 0:
            screen = self.pyboy.screen.image.convert('L').resize((80, 72))
            buf = io.BytesIO()
            screen.save(buf, format="PNG")
            img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            state_text, x, y = read_memory(self.pyboy)
            
            # Add markdown table view with REAL collision data
            markdown_view = create_detailed_map_state(self.pyboy, radius=5)
            state_text += "\n" + markdown_view
            
            # Generate Feedback
            feedback = ""
            if self.last_action == "key_press" and x == self.last_x and y == self.last_y:
                feedback = "Your last movement action did NOT change your location. You are likely walking into a wall. Try a different direction."
                self.log("warning", feedback)
            
            self.last_x = x
            self.last_y = y
            
            self.log("system", f"State: {state_text.strip()}")
            self.log("system", "Requesting AI action...")
            
            self.ai_thinking = True
            threading.Thread(target=self.ai_thread_func, args=(img_b64, state_text, feedback), daemon=True).start()

        self.root.after(16, self.update_loop) # ~60 FPS

if __name__ == "__main__":
    root = tk.Tk()
    app = PokeGUI(root)
    root.mainloop()
