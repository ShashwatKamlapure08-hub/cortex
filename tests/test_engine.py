# tests/test_engine.py
# Test Cortex Core Script Engine

import sys
import json
sys.path.append(".")

from src.engine.script_engine import generate_script
from rich import print as rprint
# add import at top
from src.utils.quality_scorer import score_script, quality_report_to_dict

def test_quality_scorer():
    print("\n" + "="*50)
    print("TEST 7 — Quality Scorer")
    print("="*50)

    raw = generate_script(
        topic="How to meditate for beginners",
        format="short",
        tone="educational"
    )

    report = score_script(raw)
    result = quality_report_to_dict(report)
    rprint(result)
    print(f"\n🏆 Overall Score: {result['overall_score']}/100 — Grade: {result['grade']}")
    print(f"✅ Passed: {result['passed']}")
    print(f"🔄 Regenerate Recommended: {result['regenerate_recommended']}")
from src.formatters.long_formatter import (
    format_long,
    production_script_to_dict as long_to_dict
)

def test_long_formatter():
    print("\n" + "="*50)
    print("TEST 6 — Long Formatter")
    print("="*50)

    raw = generate_script(
        topic="The psychology of human motivation",
        format="long",
        tone="storytelling"
    )

    production = format_long(raw)
    result = long_to_dict(production)
    rprint(result)
from src.formatters.medium_formatter import (
    format_medium,
    production_script_to_dict as medium_to_dict
)

def test_medium_formatter():
    print("\n" + "="*50)
    print("TEST 5 — Medium Formatter")
    print("="*50)

    raw = generate_script(
        topic="The future of electric vehicles",
        format="medium",
        tone="educational"
    )

    production = format_medium(raw)
    result = medium_to_dict(production)
    rprint(result)

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


from src.formatters.short_formatter import format_short, production_script_to_dict

def test_short_formatter():
    print("\n" + "="*50)
    print("TEST 4 — Short Formatter")
    print("="*50)

    # Step 1 — Generate raw script
    raw = generate_script(
        topic="How to wake up early",
        format="short",
        tone="motivational"
    )

    # Step 2 — Format it
    production = format_short(raw)
    result = production_script_to_dict(production)
    rprint(result)

if __name__ == "__main__":
    test_short_script()
    test_medium_script()
    test_long_script()
    test_short_formatter()  
    test_medium_formatter()
    test_long_formatter()
    test_quality_scorer()
