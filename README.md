# Local Model Poke

This repository contains a Python script to play Pokemon Crystal using a local LLM via LM Studio with a comprehensive prompt system for intelligent gameplay.

## Prerequisites

- Python 3.10+
- A GameBoy Color ROM file named `crystal.gbc` in the `roms/` directory.
- [LM Studio](https://lmstudio.ai/) (or compatible OpenAI API) running locally.

## Setup

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2.  Ensure your local model is running. By default, the script connects to:
    - URL: `http://10.237.108.224:1234/v1`
    - Model: `local-model`

    You can modify these settings in `main.py` under the `# Configuration` section.

3.  Test the prompt system:
    ```bash
    python test_prompts.py
    ```

## Usage

### Basic Mode (Simple Gameplay)
Run the basic agent:
```bash
python main.py
```

### Enhanced Mode (Full Prompt System)
Run the enhanced agent with all features:
```bash
python main_enhanced.py
```

The enhanced version includes:
- **System Prompt**: Main gameplay decisions
- **Self-Critic**: Periodic performance analysis (every 50 turns)
- **Knowledge Search**: Game information lookup when stuck
- **Pathfinding**: Complex navigation assistance
- **Summary**: Session summarization (every 200 turns)

### Markdown Vision Mode ⭐ NEW & RECOMMENDED
Run with structured markdown table vision and Python pathfinding:
```bash
python main_markdown.py
```

**Why use markdown vision?**
- 📊 **Clear Coordinates**: LLM can see exact (X, Y) positions in a table
- 🧮 **Python Pathfinding**: AI calculates optimal paths using A* algorithm
- 🎯 **Better Spatial Understanding**: Tables are easier for LLMs to parse than ASCII art
- 🚀 **Smarter Navigation**: AI can reference coordinates programmatically

See the markdown vision demo:
```bash
python test_markdown_vision.py
```

### View Examples
See usage examples:
```bash
python examples/prompt_usage_examples.py
```

## Prompt System

All AI prompts are stored in the `prompts/` directory:

- `system_prompt.txt` - Main gameplay instructions
- `self_critic_prompt.txt` - Performance analysis
- `summary_prompt.txt` - Session summarization
- `pathfinding_prompt.txt` - Navigation assistance
- `knowledge_search_prompt.txt` - Game knowledge lookup

See [prompts/README.md](prompts/README.md) for detailed documentation.

## Project Structure

```
local_model_poke/
├── main.py                      # Basic AI agent
├── main_enhanced.py             # Enhanced agent with full prompt system
├── main_markdown.py             # ⭐ Markdown vision agent (RECOMMENDED)
├── test_prompts.py              # Test script for prompt system
├── test_markdown_vision.py      # Demo of markdown vision
├── prompts/                     # All AI prompts
│   ├── system_prompt.txt
│   ├── self_critic_prompt.txt
│   ├── summary_prompt.txt
│   ├── pathfinding_prompt.txt
│   ├── knowledge_search_prompt.txt
│   └── README.md
├── src/
│   ├── prompt_manager.py        # Prompt loading and management
│   ├── markdown_vision.py       # ⭐ Markdown table vision system
│   ├── pathfinding_executor.py  # ⭐ Python A* pathfinding
│   ├── maps.py                  # Map data
│   ├── memory_reader.py         # Game state reading
│   ├── vision.py                # Original ASCII vision
│   └── ...
├── examples/
│   └── prompt_usage_examples.py
└── roms/
    └── crystal.gbc              # Your ROM file
```

## How It Works

1.  **Capture**: Screenshots and game state are captured from the emulator
2.  **Process**: Game state is read from memory (position, party, etc.)
3.  **Decide**: AI uses appropriate prompt to make decisions
4.  **Execute**: Actions (key presses) are sent to the emulator
5.  **Analyze**: Periodic self-criticism detects loops and errors
6.  **Summarize**: Long sessions are summarized to maintain context

## Configuration

Edit constants in `main_enhanced.py`:

```python
TURNS_BETWEEN_CRITICISM = 50   # How often to run self-analysis
SUMMARY_INTERVAL = 200         # How often to create summaries
STUCK_THRESHOLD = 5            # Position repeats before "stuck" detection
```

## Customization

Edit prompt files in `prompts/` directory to customize AI behavior. Changes take effect immediately (prompts are loaded fresh each time).
