"""
Quick test script to verify prompt system is working correctly
Run this before starting main gameplay to ensure all prompts load properly
"""

import os
import sys
from src.prompt_manager import PromptManager, PromptType

# Fix encoding for Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

def test_prompt_files_exist():
    """Test that all prompt files exist"""
    print("🔍 Checking prompt files...\n")

    prompts_dir = "prompts"
    required_files = [
        "system_prompt.txt",
        "self_critic_prompt.txt",
        "summary_prompt.txt",
        "pathfinding_prompt.txt",
        "knowledge_search_prompt.txt"
    ]

    all_exist = True
    for filename in required_files:
        filepath = os.path.join(prompts_dir, filename)
        exists = os.path.exists(filepath)
        status = "✅" if exists else "❌"
        print(f"{status} {filename}")

        if not exists:
            all_exist = False

    print()
    return all_exist


def test_prompt_loading():
    """Test that PromptManager can load all prompts"""
    print("📚 Testing prompt loading...\n")

    try:
        pm = PromptManager()

        tests = [
            ("System Prompt", pm.get_system_prompt),
            ("Self-Critic Prompt", pm.get_self_critic_prompt),
            ("Summary Prompt", pm.get_summary_prompt),
            ("Pathfinding Prompt", pm.get_pathfinding_prompt),
            ("Knowledge Search Prompt", pm.get_knowledge_search_prompt),
        ]

        all_passed = True
        for name, loader_func in tests:
            try:
                content = loader_func()
                char_count = len(content)
                print(f"✅ {name}: {char_count} characters")
            except Exception as e:
                print(f"❌ {name}: {e}")
                all_passed = False

        print()
        return all_passed

    except Exception as e:
        print(f"❌ Failed to initialize PromptManager: {e}\n")
        return False


def test_prompt_content():
    """Verify prompts have expected content"""
    print("🔎 Checking prompt content...\n")

    pm = PromptManager()

    checks = [
        ("System Prompt contains 'Pokemon'", "Pokemon" in pm.get_system_prompt()),
        ("System Prompt contains 'execute_action'", "execute_action" in pm.get_system_prompt()),
        ("Self-Critic contains 'Error Detection'", "Error Detection" in pm.get_self_critic_prompt()),
        ("Summary contains 'GAMEPLAY SUMMARY'", "GAMEPLAY SUMMARY" in pm.get_summary_prompt()),
        ("Pathfinding contains 'pathfinding'", "pathfinding" in pm.get_pathfinding_prompt().lower()),
        ("Knowledge contains 'Pokemon Red'", "Pokemon Red" in pm.get_knowledge_search_prompt()),
    ]

    all_passed = True
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
        if not result:
            all_passed = False

    print()
    return all_passed


def test_cache_system():
    """Test that caching works properly"""
    print("💾 Testing cache system...\n")

    try:
        pm = PromptManager()

        # Load once
        prompt1 = pm.get_system_prompt()

        # Load again (should be cached)
        prompt2 = pm.get_system_prompt()

        # Should be identical
        if prompt1 == prompt2:
            print("✅ Cache working: Same content returned")
        else:
            print("❌ Cache issue: Different content returned")
            return False

        # Test reload
        pm.reload_prompts()
        prompt3 = pm.get_system_prompt()

        if prompt3 == prompt1:
            print("✅ Reload working: Content consistent")
        else:
            print("❌ Reload issue: Content changed")
            return False

        print()
        return True

    except Exception as e:
        print(f"❌ Cache test failed: {e}\n")
        return False


def display_summary():
    """Display a summary of prompt sizes"""
    print("📊 Prompt Statistics:\n")

    pm = PromptManager()

    prompts = [
        ("System", pm.get_system_prompt()),
        ("Self-Critic", pm.get_self_critic_prompt()),
        ("Summary", pm.get_summary_prompt()),
        ("Pathfinding", pm.get_pathfinding_prompt()),
        ("Knowledge Search", pm.get_knowledge_search_prompt()),
    ]

    print(f"{'Prompt Type':<20} {'Characters':<12} {'Est. Tokens':<12}")
    print("-" * 44)

    total_chars = 0
    for name, content in prompts:
        chars = len(content)
        est_tokens = chars // 4  # Rough estimate: 1 token ≈ 4 characters
        total_chars += chars
        print(f"{name:<20} {chars:<12} {est_tokens:<12}")

    print("-" * 44)
    total_tokens = total_chars // 4
    print(f"{'TOTAL':<20} {total_chars:<12} {total_tokens:<12}")
    print()


def main():
    print("="*60)
    print("Pokemon Crystal AI - Prompt System Test")
    print("="*60)
    print()

    tests = [
        ("File Existence", test_prompt_files_exist),
        ("Prompt Loading", test_prompt_loading),
        ("Content Validation", test_prompt_content),
        ("Cache System", test_cache_system),
    ]

    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))

    # Display summary
    display_summary()

    # Final results
    print("="*60)
    print("Test Results:")
    print("="*60)

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False

    print("="*60)

    if all_passed:
        print("\n✅ All tests passed! Prompt system ready to use.")
        print("\nYou can now run:")
        print("  - python main.py (basic gameplay)")
        print("  - python main_enhanced.py (full prompt system)")
        print("  - python examples/prompt_usage_examples.py (examples)")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")

    print()


if __name__ == "__main__":
    main()
