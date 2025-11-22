# Pokemon Crystal AI - Prompt System

This directory contains all prompts used by the Pokemon Crystal AI agent. Each prompt serves a specific purpose in the gameplay loop.

## Prompt Files

### 1. `system_prompt.txt` - Main Gameplay Prompt
**Usage**: Active during normal gameplay
**Purpose**: Core instructions for playing Pokemon Crystal

This is the primary prompt that guides the AI through:
- Navigation and exploration
- Battle decisions
- Menu navigation
- Resource management
- Objective tracking

**When to use**: Every regular gameplay turn

---

### 2. `self_critic_prompt.txt` - Performance Analysis
**Usage**: Periodic (recommended every 50 turns)
**Purpose**: Self-analysis to detect errors and loops

Helps the AI:
- Detect stuck/loop patterns
- Identify strategic mistakes
- Analyze spatial reasoning errors
- Improve decision-making

**When to use**:
- Every N turns (50-100 recommended)
- When detecting repetitive behavior
- Before major decisions

---

### 3. `summary_prompt.txt` - Session Summarization
**Usage**: Periodic (recommended every 200 turns)
**Purpose**: Create comprehensive gameplay summary

Creates summaries including:
- Current game state
- Team composition
- Progress timeline
- Map exploration status
- Next objectives

**When to use**:
- When conversation history gets long (>200 turns)
- Before saving/loading sessions
- When switching AI instances

---

### 4. `pathfinding_prompt.txt` - Navigation Assistant
**Usage**: On-demand
**Purpose**: Calculate optimal paths through complex maps

Specialized for:
- A* pathfinding algorithms
- Obstacle avoidance
- Multi-step navigation
- Maze solving

**When to use**:
- Complex navigation required
- When stuck behind obstacles
- For long-distance travel planning
- Maze/puzzle areas

---

### 5. `knowledge_search_prompt.txt` - Game Information
**Usage**: On-demand
**Purpose**: Retrieve specific Pokemon Crystal game knowledge

Provides information about:
- Game mechanics
- Pokemon stats and locations
- Item locations
- Story progression requirements
- HM/TM usage

**When to use**:
- When stuck on progression
- Need specific game info
- Unsure about mechanics
- Planning strategy

---

## Usage in Code

### Basic Usage (main.py)
```python
from src.prompt_manager import PromptManager, PromptType

# Initialize
prompt_manager = PromptManager()

# Load system prompt for gameplay
system_prompt = prompt_manager.get_system_prompt()
```

### Advanced Usage (main_enhanced.py)
```python
# Main gameplay
system_prompt = prompt_manager.get_system_prompt()

# Periodic self-analysis (every 50 turns)
if turn_count % 50 == 0:
    critic_prompt = prompt_manager.get_self_critic_prompt()
    # Run analysis...

# When stuck
if is_stuck():
    knowledge_prompt = prompt_manager.get_knowledge_search_prompt()
    # Search for help...

# Complex navigation
if need_pathfinding():
    pathfinding_prompt = prompt_manager.get_pathfinding_prompt()
    # Calculate path...

# Session management (every 200 turns)
if turn_count % 200 == 0:
    summary_prompt = prompt_manager.get_summary_prompt()
    # Create summary...
```

---

## Customization

### Editing Prompts
1. Open the relevant `.txt` file in this directory
2. Modify the instructions as needed
3. Save the file
4. Prompts are loaded fresh each time (or use `prompt_manager.reload_prompts()`)

### Adding New Prompts
1. Create new `.txt` file in `prompts/` directory
2. Add enum entry to `PromptType` in `src/prompt_manager.py`:
   ```python
   class PromptType(Enum):
       MY_NEW_PROMPT = "my_new_prompt.txt"
   ```
3. Add helper method to `PromptManager` class:
   ```python
   def get_my_new_prompt(self) -> str:
       return self.load_prompt(PromptType.MY_NEW_PROMPT)
   ```

---

## Recommended Workflow

### For Short Sessions (< 100 turns)
```
1. Use SYSTEM_PROMPT for all gameplay
2. Run SELF_CRITIC at turn 50
3. Use KNOWLEDGE_SEARCH if stuck
```

### For Medium Sessions (100-300 turns)
```
1. Use SYSTEM_PROMPT for gameplay
2. Run SELF_CRITIC every 50 turns
3. Use PATHFINDING for complex areas
4. Run SUMMARY at turn 200
5. Use KNOWLEDGE_SEARCH as needed
```

### For Long Sessions (300+ turns)
```
1. Use SYSTEM_PROMPT for gameplay
2. Run SELF_CRITIC every 50 turns
3. Run SUMMARY every 200 turns
4. Use PATHFINDING for navigation
5. Use KNOWLEDGE_SEARCH frequently
6. Consider resetting context with summaries
```

---

## Performance Tips

### Token Management
- System prompt is ~2500 tokens
- Self-critic adds ~1000 tokens
- Summary adds ~500-1500 tokens
- Keep total context under model limits

### Frequency Tuning
Adjust these constants in `main_enhanced.py`:
```python
TURNS_BETWEEN_CRITICISM = 50   # Higher = less frequent analysis
SUMMARY_INTERVAL = 200         # Higher = less frequent summaries
STUCK_THRESHOLD = 5            # Lower = detect stuck faster
```

### Speed Optimization
- Cache prompts (default behavior)
- Use lower `max_tokens` for faster responses
- Reduce image resolution for quicker processing

---

## Troubleshooting

### Prompt Not Loading
```python
# Check if file exists
import os
print(os.path.exists("prompts/system_prompt.txt"))

# Reload prompts
prompt_manager.reload_prompts()
```

### Context Too Large
- Reduce history length in messages
- Increase SUMMARY_INTERVAL to create summaries more often
- Trim old conversation history after summarization

### AI Not Following Prompt
- Check prompt file content
- Verify prompt is being loaded correctly
- Ensure model is receiving the prompt
- Try simplifying prompt instructions

---

## Examples

See `examples/prompt_usage_examples.py` for detailed usage examples.

Run examples:
```bash
python examples/prompt_usage_examples.py
```

---

## Credits

These prompts are designed for Pokemon Crystal (Gen 2) gameplay.
Based on Gen 1 Pokemon Red mechanics with Crystal-specific adaptations.
