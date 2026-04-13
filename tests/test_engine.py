# tests/test_engine.py
# Test Cortex Core Script Engine

import sys
import json
sys.path.append(".")

from src.engine.script_engine import generate_script
from rich import print as rprint


def test_short_script():
    print("\n" + "="*50)
    print("TEST 1 — Short Script")
    print("="*50)
    result = generate_script(
        topic="How to focus better",
        format="short",
        tone="motivational"
    )
    rprint(result)


def test_medium_script():
    print("\n" + "="*50)
    print("TEST 2 — Medium Script")
    print("="*50)
    result = generate_script(
        topic="The history of artificial intelligence",
        format="medium",
        tone="educational"
    )
    rprint(result)


def test_long_script():
    print("\n" + "="*50)
    print("TEST 3 — Long Script")
    print("="*50)
    result = generate_script(
        topic="How to build a successful startup",
        format="long",
        tone="storytelling"
    )
    rprint(result)


if __name__ == "__main__":
    test_short_script()
    test_medium_script()   # uncomment this
    test_long_script()     # uncomment this
