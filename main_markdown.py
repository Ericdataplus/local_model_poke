"""
Pokemon Crystal AI with Markdown Table Vision
Uses structured markdown tables for better LLM spatial understanding
and Python code execution for pathfinding calculations.
"""

import os
import time
import base64
import io
import json
import threading
import queue
from pyboy import PyBoy
from PIL import Image
from openai import OpenAI
from src.prompt_manager import PromptManager, PromptType
from src.maps import get_map_name
from src.markdown_vision import create_detailed_map_state, create_pathfinding_data
from src.pathfinding_executor import calculate_path_from_data, execute_pathfinding_code, simplify_path

# Configuration
ROM_PATH = "roms/crystal.gbc"
SAVE_STATE = "init.state"
MODEL_NAME = "local-model"
API_BASE = "http://10.237.108.224:1234/v1"
API_KEY = "lm-studio"

# Tuning
VISION_RADIUS = 5  # How many tiles to show in each direction


class MarkdownPokemonAgent:
    """Pokemon agent with markdown table vision and Python pathfinding."""

    def __init__(self):
        self.client = OpenAI(base_url=API_BASE, api_key=API_KEY)
        self.prompt_manager = PromptManager()
        self.history = []
        self.turn_count = 0

    def get_action(self, image_base64, pyboy):
        """
        Get AI action using markdown table vision.

        Args:
            image_base64: Base64 encoded screenshot
            pyboy: PyBoy instance for reading game state

        Returns:
            OpenAI message response
        """
        try:
            # Load markdown-specific prompt
            system_prompt = self.prompt_manager.load_prompt(PromptType.SYSTEM)

            # Try to load markdown-specific prompt if it exists
            try:
                with open("prompts/system_prompt_markdown.txt", 'r', encoding='utf-8') as f:
                    system_prompt = f.read()
            except:
                pass  # Fall back to regular system prompt

            # Create markdown table state
            map_state = create_detailed_map_state(pyboy, radius=VISION_RADIUS)

            # Get basic game info
            player_x = pyboy.memory[0xDCB8]
            player_y = pyboy.memory[0xDCB7]
            map_group = pyboy.memory[0xDCB5]
            map_number = pyboy.memory[0xDCB6]
            party_count = pyboy.memory[0xDCD7]
            map_name = get_map_name(map_group, map_number)

            game_state = f"""# Game State

**Location:** {map_name}
**Coordinates:** ({player_x}, {player_y})
**Map ID:** Group {map_group}, Map {map_number}
**Party Size:** {party_count} Pokemon

{map_state}

## Instructions
Analyze the map table above. You can see:
- Your position (🧍)
- Walkable tiles (⬜)
- Obstacles (🟫)
- Exits/Doors (🚪)
- NPCs (👤)

Use this information to decide your next move. If you need to calculate a complex path, you can use Python code with the pathfinding functions provided.
"""

            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": game_state},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            },
                        },
                    ],
                },
            ]

            # Add history
            if self.history:
                messages.append({
                    "role": "assistant",
                    "content": "Previous actions:\n" + "\n".join(self.history[-15:])
                })

            print(f"⏳ Sending request to {API_BASE}...")
            start_time = time.time()

            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=self._get_tools(),
                tool_choice="auto",
                max_tokens=400,
                timeout=120.0
            )

            duration = time.time() - start_time
            print(f"✅ Response received in {duration:.2f}s")

            return response.choices[0].message

        except Exception as e:
            print(f"❌ AI Error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def calculate_path_with_python(self, target_x, target_y, pyboy):
        """
        Use Python pathfinding to calculate path to target.

        Args:
            target_x, target_y: Target coordinates
            pyboy: PyBoy instance

        Returns:
            Path result dict
        """
        print(f"\n🧮 Calculating path to ({target_x}, {target_y})...")

        # Get pathfinding data
        data = create_pathfinding_data(pyboy, target_x, target_y)

        # Calculate path
        result = calculate_path_from_data(data)

        if result['success']:
            simplified = simplify_path(result['path'])
            print(f"✅ Path found: {simplified}")
            print(f"   Distance: {result['distance']} tiles")
        else:
            print(f"❌ No path found")

        return result

    def _get_tools(self):
        """Define available tools for the AI."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "key_press",
                    "description": "Press a sequence of keys on the GameBoy.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "keys": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["up", "down", "left", "right", "a", "b", "start", "select"]
                                },
                                "description": "List of keys to press in order"
                            },
                            "reasoning": {
                                "type": "string",
                                "description": "Brief explanation of why these keys were chosen"
                            }
                        },
                        "required": ["keys"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_path",
                    "description": "Calculate optimal path to a target coordinate using Python A* algorithm.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "target_x": {
                                "type": "integer",
                                "description": "Target X coordinate from the map table"
                            },
                            "target_y": {
                                "type": "integer",
                                "description": "Target Y coordinate from the map table"
                            }
                        },
                        "required": ["target_x", "target_y"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "wait",
                    "description": "Wait for a number of frames.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "frames": {"type": "integer", "default": 60}
                        }
                    }
                }
            }
        ]


def execute_action(pyboy, tool_call, agent):
    """Execute AI action on the emulator."""
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    summary = f"{name}({json.dumps(args)})"
    print(f"🤖 AI Action: {summary}")

    if name == "key_press":
        reasoning = args.get("reasoning", "")
        if reasoning:
            print(f"   💭 Reasoning: {reasoning}")

        for key in args["keys"]:
            if key == "up": pyboy.button('up')
            elif key == "down": pyboy.button('down')
            elif key == "left": pyboy.button('left')
            elif key == "right": pyboy.button('right')
            elif key == "a": pyboy.button('a')
            elif key == "b": pyboy.button('b')
            elif key == "start": pyboy.button('start')
            elif key == "select": pyboy.button('select')
            pyboy.tick()

        for _ in range(10):
            pyboy.tick()

    elif name == "calculate_path":
        # Calculate path and execute it
        result = agent.calculate_path_with_python(
            args['target_x'],
            args['target_y'],
            pyboy
        )

        if result['success'] and result['path']:
            print(f"   Executing path: {simplify_path(result['path'])}")

            # Execute the path
            for direction in result['path']:
                if direction == "up": pyboy.button('up')
                elif direction == "down": pyboy.button('down')
                elif direction == "left": pyboy.button('left')
                elif direction == "right": pyboy.button('right')
                pyboy.tick()

                for _ in range(8):  # Small delay between moves
                    pyboy.tick()
        else:
            print("   ⚠️  Path calculation failed, no movement")

    elif name == "wait":
        frames = args.get("frames", 60)
        for _ in range(frames):
            pyboy.tick()

    return summary


def ai_thread_func(agent, img_b64, pyboy_ref, result_queue):
    """Thread function to call the AI."""
    response = agent.get_action(img_b64, pyboy_ref)
    result_queue.put(response)


def main():
    print("🎮 Starting Pokemon Crystal AI (Markdown Table Vision)...")
    print("📊 Using structured tables for better spatial understanding\n")

    if not os.path.exists(ROM_PATH):
        print(f"❌ ROM not found: {ROM_PATH}")
        return

    pyboy = PyBoy(ROM_PATH, window="SDL2")
    pyboy.set_emulation_speed(0)

    if os.path.exists(SAVE_STATE):
        with open(SAVE_STATE, "rb") as f:
            pyboy.load_state(f)

    agent = MarkdownPokemonAgent()
    frame_count = 0

    ai_queue = queue.Queue()
    ai_thinking = False

    print("✅ System ready!")
    print(f"   Vision radius: {VISION_RADIUS} tiles")
    print(f"   Pathfinding: Python A* algorithm")
    print()

    try:
        while pyboy.tick():
            time.sleep(0.01)
            frame_count += 1

            # Check for AI results
            if ai_thinking:
                try:
                    response = ai_queue.get_nowait()
                    ai_thinking = False
                    print("✅ AI Response Received!")

                    # Execute
                    if response and response.tool_calls:
                        for tool_call in response.tool_calls:
                            summary = execute_action(pyboy, tool_call, agent)
                            agent.history.append(summary)
                            if len(agent.history) > 50:
                                agent.history.pop(0)
                    elif response and response.content:
                        print(f"💭 AI Message: {response.content}")
                    else:
                        print("⏭️  AI Passed.")

                    agent.turn_count += 1

                except queue.Empty:
                    pass

            # Start new AI task
            if not ai_thinking and frame_count % 60 == 0:
                # Capture image (smaller for speed)
                screen = pyboy.screen.image.convert('L').resize((80, 72))
                buf = io.BytesIO()
                screen.save(buf, format="PNG")
                img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

                # Get position for logging
                player_x = pyboy.memory[0xDCB8]
                player_y = pyboy.memory[0xDCB7]
                map_group = pyboy.memory[0xDCB5]
                map_number = pyboy.memory[0xDCB6]
                map_name = get_map_name(map_group, map_number)

                print(f"\n📍 Turn {agent.turn_count + 1}: {map_name} ({player_x}, {player_y})")

                ai_thinking = True
                threading.Thread(
                    target=ai_thread_func,
                    args=(agent, img_b64, pyboy, ai_queue),
                    daemon=True
                ).start()

    except KeyboardInterrupt:
        pyboy.stop()
        print("\n👋 Stopped by user")
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pyboy.stop()


if __name__ == "__main__":
    main()
