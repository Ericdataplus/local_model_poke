# Quick Start Guide - Pokemon Crystal AI

## 1. Verify Setup ✅

```bash
# Test that all prompts are working
python test_prompts.py
```

You should see all green checkmarks.

---

## 2. Choose Your Mode

### Option A: Basic Mode (Recommended for Testing)
Simple gameplay with just the system prompt.

```bash
python main.py
```

**Good for:**
- Testing your LM Studio connection
- Quick gameplay sessions
- Learning how the system works

---

### Option B: Enhanced Mode (Full Features)
Complete prompt system with self-analysis and knowledge search.

```bash
python main_enhanced.py
```

**Features:**
- ✅ Main gameplay (system prompt)
- 🔍 Self-criticism every 50 turns
- 📚 Knowledge search when stuck
- 🧭 Pathfinding assistance
- 📝 Session summaries every 200 turns

---

## 3. Configuration

Before running, verify your LM Studio settings in the script:

```python
# In main.py or main_enhanced.py
API_BASE = "http://10.237.108.224:1234/v1"  # Your LM Studio URL
MODEL_NAME = "local-model"                    # Your model name
```

---

## 4. What to Expect

### First Run
```
🎮 Starting Pokemon Crystal AI...
📚 Full Prompt System Loaded

⏳ Sending request to http://...
✅ Response received in 3.45s
📊 State: Location: New Bark Town (1, 1) at (10, 12)
🤖 AI Action: key_press({'keys': ['up', 'up', 'up']})
```

### During Gameplay
- Every turn: AI makes decisions using the system prompt
- Every 50 turns: Self-criticism analysis runs
- When stuck: Knowledge search activates
- Every 200 turns: Session summary created

---

## 5. Monitoring Progress

### Check the Console
Watch for these indicators:
- `🤖 AI Action:` - What the AI decided to do
- `📊 State:` - Current game position
- `⚠️ STUCK DETECTED:` - AI detected it's looping
- `🔍 Running self-criticism...` - Analysis in progress

### Check run_log.txt
Actions are logged for later review.

---

## 6. Customizing Behavior

### Quick Tweaks (main_enhanced.py)
```python
# How often to run self-analysis
TURNS_BETWEEN_CRITICISM = 50  # Default: 50, Range: 25-100

# How often to create summaries
SUMMARY_INTERVAL = 200  # Default: 200, Range: 100-500

# How many position repeats = stuck
STUCK_THRESHOLD = 5  # Default: 5, Range: 3-10
```

### Deep Customization (prompts/)
Edit any `.txt` file in the `prompts/` directory:
- `system_prompt.txt` - Change core gameplay strategy
- `self_critic_prompt.txt` - Adjust self-analysis criteria
- `pathfinding_prompt.txt` - Modify navigation logic
- etc.

Changes take effect immediately (no restart needed).

---

## 7. Troubleshooting

### "Connection refused"
- Make sure LM Studio is running
- Verify the API_BASE URL is correct
- Check that your model is loaded in LM Studio

### "ROM not found"
```bash
# Create roms directory
mkdir roms

# Add your crystal.gbc file to roms/
```

### AI is stuck in a loop
The enhanced mode should detect this automatically after 5 repeats.
If not, lower `STUCK_THRESHOLD` in main_enhanced.py.

### Context too large / Out of memory
- Reduce `SUMMARY_INTERVAL` to create summaries more often
- Use a smaller image size in the capture code
- Trim conversation history more aggressively

---

## 8. Performance Tips

### Speed Up Responses
```python
# In get_action() method
max_tokens=150,  # Lower = faster but less detailed
```

### Reduce Token Usage
```python
# In main loop
screen = pyboy.screen.image.convert('L').resize((60, 54))  # Smaller image
agent.history[-10:]  # Shorter history
```

### Balance Quality vs Speed
| Setting | Speed | Intelligence | Tokens |
|---------|-------|--------------|--------|
| Conservative | ⚡⚡⚡ | ⭐⭐ | 💰 |
| Balanced | ⚡⚡ | ⭐⭐⭐ | 💰💰 |
| Maximum | ⚡ | ⭐⭐⭐⭐ | 💰💰💰 |

---

## 9. File Structure

```
local_model_poke/
├── main.py              ← Start here (basic)
├── main_enhanced.py     ← Or here (full features)
├── test_prompts.py      ← Run this first
├── prompts/             ← Edit these to customize
│   ├── system_prompt.txt
│   ├── self_critic_prompt.txt
│   ├── summary_prompt.txt
│   ├── pathfinding_prompt.txt
│   └── knowledge_search_prompt.txt
└── run_log.txt          ← Check this for history
```

---

## 10. Next Steps

1. ✅ Run `python test_prompts.py`
2. ✅ Start with `python main.py` for basic test
3. ✅ Try `python main_enhanced.py` for full features
4. ✅ Watch the console output
5. ✅ Customize prompts in `prompts/` directory
6. ✅ Adjust tuning parameters in main_enhanced.py
7. ✅ Check examples in `examples/prompt_usage_examples.py`

---

## Quick Reference

| Task | Command |
|------|---------|
| Test prompts | `python test_prompts.py` |
| Basic gameplay | `python main.py` |
| Full features | `python main_enhanced.py` |
| See examples | `python examples/prompt_usage_examples.py` |
| Edit system prompt | Edit `prompts/system_prompt.txt` |
| Edit analysis | Edit `prompts/self_critic_prompt.txt` |
| View documentation | See `prompts/README.md` |

---

**Happy gaming! 🎮**
