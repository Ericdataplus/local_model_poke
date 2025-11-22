"""
Examples of how to use different prompts with the Pokemon Crystal AI Agent

This file demonstrates how to invoke different prompt types for various scenarios:
- System Prompt: Main gameplay loop
- Pathfinding: Navigation assistance
- Knowledge Search: Game information lookup
- Self-Critic: Periodic self-analysis
- Summary: Session summarization
"""

from src.prompt_manager import PromptManager, PromptType
from openai import OpenAI

# Configuration
API_BASE = "http://10.237.108.224:1234/v1"
API_KEY = "lm-studio"
MODEL_NAME = "local-model"

# Initialize
prompt_manager = PromptManager()
client = OpenAI(base_url=API_BASE, api_key=API_KEY)


def example_main_gameplay():
    """
    Example: Main gameplay loop with system prompt
    This is what main.py uses for regular gameplay
    """
    print("=== EXAMPLE 1: Main Gameplay ===\n")

    system_prompt = prompt_manager.get_system_prompt()
    game_state = "Location: New Bark Town at (10, 12)\nParty Count: 1"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"GAME STATE:\n{game_state}\n\nWhat should I do next?"}
    ]

    # This would call the AI
    print(f"System Prompt Length: {len(system_prompt)} characters")
    print("Ready to send to AI for action decision\n")


def example_pathfinding_request():
    """
    Example: Request pathfinding assistance
    Use when you need the AI to calculate a specific path
    """
    print("=== EXAMPLE 2: Pathfinding Request ===\n")

    pathfinding_prompt = prompt_manager.get_pathfinding_prompt()

    # Example map data (simplified)
    map_data = """
    Current Position: (5, 5)
    Target Position: (15, 10)

    Map Layout:
    🟫🟫🟫⛔⛔🟫🟫🟫
    🟫🟫🟫⛔⛔🟫🟫🟫
    🟫🟫🟫🟫🟫🟫🟫🟫
    🟫🌿🌿🌿🌿🟫🟫🟫
    🟫🌿🌿🌿🌿🟫🟫🟫
    """

    messages = [
        {"role": "system", "content": pathfinding_prompt},
        {"role": "user", "content": f"Calculate path:\n{map_data}"}
    ]

    print("Pathfinding prompt loaded")
    print("Ready to request path calculation\n")


def example_knowledge_search():
    """
    Example: Search for game knowledge
    Use when stuck or need specific game information
    """
    print("=== EXAMPLE 3: Knowledge Search ===\n")

    knowledge_prompt = prompt_manager.get_knowledge_search_prompt()

    query = "How do I get to the Pokemon League in Crystal? What badges do I need?"

    messages = [
        {"role": "system", "content": knowledge_prompt},
        {"role": "user", "content": query}
    ]

    print(f"Knowledge Query: {query}")
    print("Ready to search game knowledge\n")


def example_self_criticism():
    """
    Example: Periodic self-analysis
    Use every N turns to analyze performance and detect loops
    """
    print("=== EXAMPLE 4: Self-Criticism Analysis ===\n")

    critic_prompt = prompt_manager.get_self_critic_prompt()

    recent_history = """
    Recent Actions:
    1. Moved north 3 times
    2. Encountered wild Pokemon
    3. Moved south 3 times
    4. Moved north 3 times
    5. Encountered wild Pokemon
    6. Moved south 3 times

    Current Objective: Reach Route 30
    """

    messages = [
        {"role": "system", "content": critic_prompt},
        {"role": "user", "content": f"Analyze my recent gameplay:\n{recent_history}"}
    ]

    print("Self-critic prompt loaded")
    print("This would detect the loop pattern in the actions\n")


def example_session_summary():
    """
    Example: Create session summary
    Use when conversation gets too long or before saving state
    """
    print("=== EXAMPLE 5: Session Summary ===\n")

    summary_prompt = prompt_manager.get_summary_prompt()

    session_data = """
    Session started in New Bark Town
    - Received starter Pokemon (Totodile)
    - Completed first trainer battle
    - Explored Route 29
    - Reached Cherrygrove City
    - Visited Pokemon Center
    - Currently: Exploring northern area of Cherrygrove

    Team:
    - Totodile (Lv 7) - Scratch, Leer, Water Gun

    Items:
    - Potion x3
    - Poké Ball x5
    """

    messages = [
        {"role": "system", "content": summary_prompt},
        {"role": "user", "content": f"Summarize this session:\n{session_data}"}
    ]

    print("Summary prompt loaded")
    print("Ready to create comprehensive session summary\n")


def example_combined_usage():
    """
    Example: How different prompts work together in a real session
    """
    print("=== EXAMPLE 6: Combined Usage in Practice ===\n")

    print("Turn 1-50: Use SYSTEM_PROMPT for normal gameplay")
    print("  └─> AI makes decisions, executes actions")
    print()
    print("Turn 25: Detect potential stuck/loop")
    print("  └─> Switch to SELF_CRITIC_PROMPT")
    print("  └─> AI analyzes recent actions, detects loop")
    print("  └─> Updates strategy")
    print()
    print("Turn 30: AI doesn't know how to progress")
    print("  └─> Switch to KNOWLEDGE_SEARCH_PROMPT")
    print("  └─> Query: 'How do I get Cut HM in Crystal?'")
    print("  └─> Get specific instructions")
    print()
    print("Turn 45: Need to navigate complex maze")
    print("  └─> Switch to PATHFINDING_PROMPT")
    print("  └─> AI calculates optimal path")
    print("  └─> Returns key sequence")
    print()
    print("Turn 100: Conversation getting long")
    print("  └─> Use SUMMARY_PROMPT")
    print("  └─> Create comprehensive summary")
    print("  └─> Start fresh with summary as context")
    print()


if __name__ == "__main__":
    print("Pokemon Crystal AI - Prompt Usage Examples\n")
    print("=" * 50)
    print()

    example_main_gameplay()
    example_pathfinding_request()
    example_knowledge_search()
    example_self_criticism()
    example_session_summary()
    example_combined_usage()

    print("=" * 50)
    print("\nAll prompts are loaded from the prompts/ directory")
    print("Edit the .txt files to customize AI behavior")
