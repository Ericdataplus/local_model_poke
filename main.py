import os
import time
import base64
import io
import threading
import queue
from pyboy import PyBoy
from pyboy.utils import WindowEvent
from PIL import Image
from openai import OpenAI
from src.prompt_manager import PromptManager, PromptType

# Configuration
ROM_PATH = "roms/crystal.gbc"
SAVE_STATE = "init.state"
MODEL_NAME = "local-model"
API_BASE = "http://10.237.108.224:1234/v1"
API_KEY = "lm-studio"

# Initialize Prompt Manager
prompt_manager = PromptManager()

class PokemonAgent:
    def __init__(self):
        self.client = OpenAI(base_url=API_BASE, api_key=API_KEY)
        self.history = []
        self.prompt_manager = prompt_manager

    def get_action(self, image_base64, game_state):
        try:
            # Load the comprehensive system prompt
            system_prompt = self.prompt_manager.get_system_prompt()

            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"GAME STATE:\n{game_state}"},
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
                messages.append({"role": "assistant", "content": "Previous actions:\n" + "\n".join(self.history[-25:])})

            print(f"⏳ Sending request to {API_BASE}...")
            start_time = time.time()
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=[{
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
                                    }
                                }
                            },
                            "required": ["keys"]
                        }
                    }
                }, {
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
                }],
                tool_choice="auto",
                max_tokens=150,
                timeout=120.0
            )
            duration = time.time() - start_time
            print(f"✅ Response received in {duration:.2f}s")

            return response.choices[0].message

        except Exception as e:
            print(f"❌ AI Error: {e}")
            return None

from src.maps import get_map_name

def read_memory(pyboy):
    """Simple memory reader for essential state."""
    # Coordinates
    x = pyboy.memory[0xDCB8]
    y = pyboy.memory[0xDCB7]
    map_group = pyboy.memory[0xDCB5]
    map_number = pyboy.memory[0xDCB6]
    
    # Party
    party_count = pyboy.memory[0xDCD7]
    
    map_name = get_map_name(map_group, map_number)
    info = f"Location: {map_name} ({map_group}, {map_number}) at ({x}, {y})\n"
    info += f"Party Count: {party_count}\n"
    
    return info

def execute_action(pyboy, tool_call):
    name = tool_call.function.name
    import json
    args = json.loads(tool_call.function.arguments)
    
    summary = f"{name}({args})"
    print(f"🤖 AI Action: {summary}")
    
    if name == "key_press":
        for key in args["keys"]:
            if key == "up": pyboy.button('up')
            elif key == "down": pyboy.button('down')
            elif key == "left": pyboy.button('left')
            elif key == "right": pyboy.button('right')
            elif key == "a": pyboy.button('a')
            elif key == "b": pyboy.button('b')
            elif key == "start": pyboy.button('start')
            elif key == "select": pyboy.button('select')
            pyboy.tick() # Hold for 1 frame
            
        # Wait a bit after input
        for _ in range(10): pyboy.tick()
        
    elif name == "wait":
        frames = args.get("frames", 60)
        for _ in range(frames): pyboy.tick()

    return summary

def ai_thread_func(agent, img_b64, state_text, result_queue):
    """Thread function to call the AI."""
    response = agent.get_action(img_b64, state_text)
    result_queue.put(response)

def main():
    print("🎮 Starting Simplified Pokemon Crystal AI (Async Mode)...")
    
    if not os.path.exists(ROM_PATH):
        print(f"❌ ROM not found: {ROM_PATH}")
        return

    pyboy = PyBoy(ROM_PATH, window="SDL2")
    pyboy.set_emulation_speed(0) # Unlimited speed
    
    if os.path.exists(SAVE_STATE):
        with open(SAVE_STATE, "rb") as f:
            pyboy.load_state(f)
            
    agent = PokemonAgent()
    frame_count = 0
    
    ai_queue = queue.Queue()
    ai_thinking = False
    
    try:
        while pyboy.tick():
            time.sleep(0.01) # Prevent high CPU usage
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
                            summary = execute_action(pyboy, tool_call)
                            agent.history.append(summary)
                            if len(agent.history) > 50: agent.history.pop(0)
                    elif response and response.content:
                        print(f"AI Message: {response.content}")
                    else:
                        print("AI Passed.")
                        
                except queue.Empty:
                    pass # Still thinking
            
            # Start new AI task if not thinking and time to act
            if not ai_thinking and frame_count % 60 == 0:
                # 1. Capture Image (Reduced size for speed)
                screen = pyboy.screen.image.convert('L').resize((80, 72))
                buf = io.BytesIO()
                screen.save(buf, format="PNG")
                img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                
                # 2. Read Memory
                state_text = read_memory(pyboy)
                print(f"📊 State: {state_text.strip()}")
                
                # 3. Start AI Thread
                ai_thinking = True
                threading.Thread(target=ai_thread_func, args=(agent, img_b64, state_text, ai_queue), daemon=True).start()
                    
    except KeyboardInterrupt:
        pyboy.stop()
        print("Stopped.")
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pyboy.stop()

if __name__ == "__main__":
    main()
