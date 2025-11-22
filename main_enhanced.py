"""
Enhanced Pokemon Crystal AI with Full Prompt System
Demonstrates integration of all prompt types:
- System: Main gameplay
- Self-Critic: Periodic analysis (every 50 turns)
- Knowledge Search: On-demand when stuck
- Pathfinding: Complex navigation
- Summary: Long session management
"""

import os
import time
import base64
import io
import threading
import queue
from pyboy import PyBoy
from PIL import Image
from openai import OpenAI
from src.prompt_manager import PromptManager, PromptType
from src.maps import get_map_name

# Configuration
ROM_PATH = "roms/crystal.gbc"
SAVE_STATE = "init.state"
MODEL_NAME = "local-model"
API_BASE = "http://10.237.108.224:1234/v1"
API_KEY = "lm-studio"

# Tuning parameters
TURNS_BETWEEN_CRITICISM = 50  # Run self-critic every N turns
STUCK_THRESHOLD = 5  # Same position N times = stuck
SUMMARY_INTERVAL = 200  # Summarize every N turns


class EnhancedPokemonAgent:
    """Pokemon agent with full prompt system support"""

    def __init__(self):
        self.client = OpenAI(base_url=API_BASE, api_key=API_KEY)
        self.prompt_manager = PromptManager()
        self.history = []
        self.turn_count = 0
        self.position_history = []
        self.last_summary = ""

    def get_action(self, image_base64, game_state):
        """Main gameplay action using system prompt"""
        try:
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
                messages.append({
                    "role": "assistant",
                    "content": "Previous actions:\n" + "\n".join(self.history[-25:])
                })

            print(f"⏳ Sending request to {API_BASE}...")
            start_time = time.time()

            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=self._get_tools(),
                tool_choice="auto",
                max_tokens=300,
                timeout=120.0
            )

            duration = time.time() - start_time
            print(f"✅ Response received in {duration:.2f}s")

            return response.choices[0].message

        except Exception as e:
            print(f"❌ AI Error: {e}")
            return None

    def run_self_criticism(self):
        """Analyze recent performance for loops and errors"""
        print("\n🔍 Running self-criticism analysis...")

        try:
            critic_prompt = self.prompt_manager.get_self_critic_prompt()

            recent_actions = "\n".join(self.history[-50:]) if self.history else "No actions yet"
            recent_positions = self.position_history[-20:] if self.position_history else []

            analysis_data = f"""
Recent Actions (last 50):
{recent_actions}

Recent Positions (last 20):
{recent_positions}

Turn Count: {self.turn_count}
"""

            messages = [
                {"role": "system", "content": critic_prompt},
                {"role": "user", "content": f"Analyze my recent gameplay:\n{analysis_data}"}
            ]

            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                max_tokens=500,
                timeout=60.0
            )

            analysis = response.choices[0].message.content
            print(f"\n📊 Self-Criticism Result:\n{analysis}\n")

            return analysis

        except Exception as e:
            print(f"❌ Self-criticism error: {e}")
            return None

    def search_knowledge(self, query):
        """Search game knowledge for help when stuck"""
        print(f"\n📚 Knowledge search: {query}")

        try:
            knowledge_prompt = self.prompt_manager.get_knowledge_search_prompt()

            messages = [
                {"role": "system", "content": knowledge_prompt},
                {"role": "user", "content": query}
            ]

            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                max_tokens=400,
                timeout=60.0
            )

            result = response.choices[0].message.content
            print(f"\n💡 Knowledge Result:\n{result}\n")

            return result

        except Exception as e:
            print(f"❌ Knowledge search error: {e}")
            return None

    def create_summary(self):
        """Create session summary for context management"""
        print("\n📝 Creating session summary...")

        try:
            summary_prompt = self.prompt_manager.get_summary_prompt()

            session_data = f"""
Turn Count: {self.turn_count}

Recent Actions:
{chr(10).join(self.history[-100:])}

Position History:
{self.position_history[-50:]}

Previous Summary:
{self.last_summary if self.last_summary else "First session"}
"""

            messages = [
                {"role": "system", "content": summary_prompt},
                {"role": "user", "content": f"Summarize this session:\n{session_data}"}
            ]

            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                max_tokens=800,
                timeout=90.0
            )

            summary = response.choices[0].message.content
            self.last_summary = summary
            print(f"\n📋 Summary Created:\n{summary}\n")

            return summary

        except Exception as e:
            print(f"❌ Summary error: {e}")
            return None

    def check_if_stuck(self, current_pos):
        """Check if we're stuck in a loop"""
        self.position_history.append(current_pos)

        # Keep last 20 positions
        if len(self.position_history) > 20:
            self.position_history.pop(0)

        # Count how many times we've been at current position recently
        recent_count = self.position_history[-10:].count(current_pos)

        if recent_count >= STUCK_THRESHOLD:
            print(f"⚠️  STUCK DETECTED: Position {current_pos} visited {recent_count} times")
            return True

        return False

    def _get_tools(self):
        """Define available tools for the AI"""
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
                                }
                            }
                        },
                        "required": ["keys"]
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


def read_memory(pyboy):
    """Read essential game state from memory"""
    x = pyboy.memory[0xDCB8]
    y = pyboy.memory[0xDCB7]
    map_group = pyboy.memory[0xDCB5]
    map_number = pyboy.memory[0xDCB6]
    party_count = pyboy.memory[0xDCD7]

    map_name = get_map_name(map_group, map_number)
    info = f"Location: {map_name} ({map_group}, {map_number}) at ({x}, {y})\n"
    info += f"Party Count: {party_count}\n"

    return info, (x, y)


def execute_action(pyboy, tool_call):
    """Execute AI action on the emulator"""
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
            pyboy.tick()

        for _ in range(10):
            pyboy.tick()

    elif name == "wait":
        frames = args.get("frames", 60)
        for _ in range(frames):
            pyboy.tick()

    return summary


def ai_thread_func(agent, img_b64, state_text, result_queue):
    """Thread function to call the AI"""
    response = agent.get_action(img_b64, state_text)
    result_queue.put(response)


def main():
    print("🎮 Starting Enhanced Pokemon Crystal AI...")
    print("📚 Full Prompt System Loaded\n")

    if not os.path.exists(ROM_PATH):
        print(f"❌ ROM not found: {ROM_PATH}")
        return

    pyboy = PyBoy(ROM_PATH, window="SDL2")
    pyboy.set_emulation_speed(0)

    if os.path.exists(SAVE_STATE):
        with open(SAVE_STATE, "rb") as f:
            pyboy.load_state(f)

    agent = EnhancedPokemonAgent()
    frame_count = 0

    ai_queue = queue.Queue()
    ai_thinking = False

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
                            summary = execute_action(pyboy, tool_call)
                            agent.history.append(summary)
                            if len(agent.history) > 100:
                                agent.history.pop(0)
                    elif response and response.content:
                        print(f"AI Message: {response.content}")
                    else:
                        print("AI Passed.")

                    agent.turn_count += 1

                    # Periodic tasks
                    if agent.turn_count % TURNS_BETWEEN_CRITICISM == 0:
                        agent.run_self_criticism()

                    if agent.turn_count % SUMMARY_INTERVAL == 0:
                        agent.create_summary()

                except queue.Empty:
                    pass

            # Start new AI task
            if not ai_thinking and frame_count % 60 == 0:
                screen = pyboy.screen.image.convert('L').resize((80, 72))
                buf = io.BytesIO()
                screen.save(buf, format="PNG")
                img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

                state_text, position = read_memory(pyboy)
                print(f"📊 State: {state_text.strip()}")

                # Check if stuck
                if agent.check_if_stuck(position):
                    print("🆘 Requesting knowledge search...")
                    agent.search_knowledge("I seem stuck. What should I do in this situation?")

                ai_thinking = True
                threading.Thread(
                    target=ai_thread_func,
                    args=(agent, img_b64, state_text, ai_queue),
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
