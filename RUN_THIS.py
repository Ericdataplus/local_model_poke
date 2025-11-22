"""
MAIN ENTRY POINT - Run this file!
Uses markdown vision with proper one-move-at-a-time execution
"""

import os
import sys

# Fix encoding for Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

print("=" * 60)
print("POKEMON CRYSTAL AI - MARKDOWN VISION MODE")
print("=" * 60)
print()
print("✅ Using: Markdown tables + Python pathfinding")
print("✅ Vision: Coordinate-based with exact positions")
print("✅ Navigation: One tile at a time (no diagonal confusion)")
print()
print("=" * 60)
print()

# Import and run the markdown main
exec(open("main_markdown.py").read())
