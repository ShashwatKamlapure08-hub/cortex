# src/formatters/medium_formatter.py
# Cortex — Medium Formatter
# Takes a raw medium script and converts it into a
# production-ready teleprompter script with chapter
# markers, B-roll suggestions, and timestamps

from dataclasses import dataclass
from typing import List, Optional


# --- Data Structures ---

@dataclass
class Segment:
    """Represents a single segment in the video."""
    segment_number: int
    type: str               # intro / section / conclusion / cta
    title: str
    timestamp_start: str
    timestamp_end: str
    duration_seconds: int
    teleprompter_text: str  # clean text for reading on camera
    broll_suggestions: List[str]  # what footage to show
    key_points: List[str]   # bullet points to display on screen
    transition: str         # how to transition to next segment


@dataclass
class MediumProductionScript:
    """Complete production-ready breakdown for a medium YouTube video."""
    title: str
    topic: str
    tone: str
    total_duration: str
    description: str
    chapters: List[dict]        # YouTube chapter markers
    segments: List[Segment]
    thumbnail_idea: str
    end_screen_suggestion: str
    tags: List[str]
    model_used: str
    cortex_version: str


# --- Helper Functions ---

def seconds_to_timestamp(seconds: int) -> str:
    """Convert seconds to MM:SS format."""
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"


def extract_text(field) -> str:
    """
    Safely extract text from a field that might be
    a plain string or a dict with a 'text' key.
    Handles both formats defensively.
    """
    if isinstance(field, dict):
        return field.get("text", str(field))
    return str(field)


def estimate_duration(text: str, words_per_minute: int = 130) -> int:
    """
    Estimate how long it takes to read text out loud.
    Average speaking pace is around 130 words per minute.
    Returns duration in seconds.
    """
    word_count = len(text.split())
    minutes = word_count / words_per_minute
    return max(30, int(minutes * 60))  # minimum 30 seconds


def generate_broll(title: str, content: str) -> List[str]:
    """Generate B-roll footage suggestions based on section content."""
    suggestions = [
        f"Relevant footage or animation related to '{title}'",
        "Text overlay with key statistics or facts mentioned",
        "Transition animation between points",
        "Close-up shots of any products, tools, or concepts mentioned"
    ]
    # Add content-specific suggestions based on keywords
    keywords = {
        "history": ["archival footage", "timeline animation", "historical photos"],
        "technology": ["tech product shots", "code on screen", "data visualizations"],
        "business": ["office environment", "team collaboration", "growth charts"],
        "science": ["lab footage", "scientific diagrams", "nature shots"],
        "health": ["fitness footage", "healthy food shots", "medical animations"],
        "money": ["financial charts", "currency visuals", "investment graphs"]
    }
    content_lower = (title + " " + content).lower()
    for keyword, extra_suggestions in keywords.items():
        if keyword in content_lower:
            suggestions.extend(extra_suggestions[:2])
            break

    return suggestions[:4]  # return max 4 suggestions


def extract_key_points(content: str, max_points: int = 3) -> List[str]:
    """
    Extract key points from section content for on-screen display.
    Splits content into sentences and picks the most impactful ones.
    """
    sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 20]
    key_points = []
    for sentence in sentences[:max_points]:
        words = sentence.split()
        if len(words) > 10:
            point = " ".join(words[:10]) + "..."
        else:
            point = sentence
        key_points.append(f"• {point}")

    return key_points if key_points else ["• Key insight from this section"]


def generate_transition(current_type: str, next_type: str) -> str:
    """Generate a transition suggestion between segments."""
    transitions = {
        ("intro", "section"): "Smooth cut with upbeat music sting — begin main content",
        ("section", "section"): "Quick fade to black, then fade in — chapter title card appears",
        ("section", "conclusion"): "Slow fade with reflective music — signal wrap-up",
        ("conclusion", "cta"): "Direct cut — increase energy, face camera directly",
        ("cta", "end"): "Fade out with subscribe animation overlay"
    }
    return transitions.get(
        (current_type, next_type),
        "Smooth cut to next segment"
    )


def generate_description(topic: str, sections: list, cta_text: str) -> str:
    """Generate a YouTube video description."""
    section_titles = "\n".join(
        [f"• {s.get('title', f'Section {i+1}')}"
         for i, s in enumerate(sections)]
    )
    return (
        f"In this video, we explore {topic}.\n\n"
        f"What we cover:\n{section_titles}\n\n"
        f"{cta_text}\n\n"
        f"Generated by Cortex — Multi-Format Script Engine"
    )


def generate_tags(topic: str, tone: str) -> List[str]:
    """Generate YouTube tags."""
    base_tags = ["educational", "youtube", "content creation"]
    tone_tags = {
        "educational": ["learn", "tutorial", "explained", "guide"],
        "motivational": ["motivation", "inspiration", "mindset", "success"],
        "storytelling": ["story", "narrative", "journey", "experience"],
        "funny": ["comedy", "humor", "entertaining", "fun"],
        "informative": ["facts", "information", "breakdown", "analysis"]
    }
    topic_tags = [w.lower() for w in topic.split() if len(w) > 3][:5]
    selected = tone_tags.get(tone, ["content", "video"])
    return list(set(base_tags + selected + topic_tags))


def generate_thumbnail_idea(topic: str, hook: str) -> str:
    """Generate a thumbnail concept."""
    hook_preview = " ".join(extract_text(hook).split()[:6]).upper()
    return (
        f"Split-screen thumbnail: Left side shows the PROBLEM "
        f"(dark, dramatic), right side shows the SOLUTION (bright, hopeful). "
        f"Bold text overlay: '{hook_preview}'. "
        f"Topic: '{topic}' — use visuals that immediately communicate the subject."
    )


def generate_end_screen(topic: str) -> str:
    """Generate end screen suggestion."""
    return (
        f"Show end screen for last 20 seconds: "
        f"Subscribe button (left), recommended video about '{topic}' (right), "
        f"channel logo (center). Add upbeat outro music."
    )


# --- Main Formatter Function ---

def format_medium(raw_script: dict) -> MediumProductionScript:
    """
    Main formatter function.
    Takes raw Cortex script output and returns a
    production-ready MediumProductionScript.

    Args:
        raw_script: dict output from generate_script() with format='medium'

    Returns:
        MediumProductionScript with full segment breakdown
    """

    # --- Validate input ---
    if raw_script.get("format") != "medium":
        raise ValueError(
            f"Expected format 'medium', got '{raw_script.get('format')}'. "
            f"Use the correct formatter for your script format."
        )

    required_keys = ["topic", "hook", "intro", "sections", "conclusion", "cta"]
    for key in required_keys:
        if key not in raw_script:
            raise ValueError(f"Missing required field '{key}' in script.")

    # --- Extract fields defensively ---
    topic = raw_script["topic"]
    hook_text = extract_text(raw_script["hook"])
    intro_text = extract_text(raw_script["intro"])
    sections = raw_script["sections"]
    conclusion_text = extract_text(raw_script["conclusion"])
    cta_text = extract_text(raw_script["cta"])
    tone = raw_script.get("metadata", {}).get("tone", "educational")
    model_used = raw_script.get("metadata", {}).get("model_used", "unknown")

    # --- Build segments ---
    segments = []
    current_second = 0
    youtube_chapters = []

    # Segment 1 — Hook + Intro
    intro_duration = estimate_duration(hook_text + " " + intro_text)
    segments.append(Segment(
        segment_number=1,
        type="intro",
        title="Introduction",
        timestamp_start=seconds_to_timestamp(current_second),
        timestamp_end=seconds_to_timestamp(current_second + intro_duration),
        duration_seconds=intro_duration,
        teleprompter_text=f"{hook_text}\n\n{intro_text}",
        broll_suggestions=[
            "Channel intro animation plays",
            "Cinematic title card with topic name",
            "Background footage relevant to the topic",
            "Creator on camera for first 10 seconds"
        ],
        key_points=[f"• Today we're covering: {topic}"],
        transition=generate_transition("intro", "section")
    ))
    youtube_chapters.append({
        "timestamp": seconds_to_timestamp(current_second),
        "title": "Introduction"
    })
    current_second += intro_duration

    # Segments — Main Sections
    for i, section in enumerate(sections):
        section_title = section.get("title", f"Section {i+1}")
        section_content = section.get("content", "")
        section_duration = estimate_duration(section_content)

        next_type = "section" if i < len(sections) - 1 else "conclusion"

        segments.append(Segment(
            segment_number=i + 2,
            type="section",
            title=section_title,
            timestamp_start=seconds_to_timestamp(current_second),
            timestamp_end=seconds_to_timestamp(current_second + section_duration),
            duration_seconds=section_duration,
            teleprompter_text=section_content,
            broll_suggestions=generate_broll(section_title, section_content),
            key_points=extract_key_points(section_content),
            transition=generate_transition("section", next_type)
        ))
        youtube_chapters.append({
            "timestamp": seconds_to_timestamp(current_second),
            "title": section_title
        })
        current_second += section_duration

    # Conclusion segment
    conclusion_duration = estimate_duration(conclusion_text)
    segments.append(Segment(
        segment_number=len(segments) + 1,
        type="conclusion",
        title="Conclusion",
        timestamp_start=seconds_to_timestamp(current_second),
        timestamp_end=seconds_to_timestamp(current_second + conclusion_duration),
        duration_seconds=conclusion_duration,
        teleprompter_text=conclusion_text,
        broll_suggestions=[
            "Montage of key moments from the video",
            "Recap text overlays of main points",
            "Uplifting background music starts"
        ],
        key_points=extract_key_points(conclusion_text, max_points=2),
        transition=generate_transition("conclusion", "cta")
    ))
    youtube_chapters.append({
        "timestamp": seconds_to_timestamp(current_second),
        "title": "Conclusion"
    })
    current_second += conclusion_duration

    # CTA segment
    cta_duration = estimate_duration(cta_text)
    segments.append(Segment(
        segment_number=len(segments) + 1,
        type="cta",
        title="Call to Action",
        timestamp_start=seconds_to_timestamp(current_second),
        timestamp_end=seconds_to_timestamp(current_second + cta_duration),
        duration_seconds=cta_duration,
        teleprompter_text=cta_text,
        broll_suggestions=[
            "Creator faces camera directly",
            "Subscribe button animation overlay",
            "End screen begins appearing"
        ],
        key_points=["• Subscribe for more content", "• Leave a comment below"],
        transition=generate_transition("cta", "end")
    ))
    current_second += cta_duration

    # --- Build final production script ---
    total_minutes = current_second // 60
    total_seconds = current_second % 60

    production_script = MediumProductionScript(
        title=f"Cortex Medium: {topic}",
        topic=topic,
        tone=tone,
        total_duration=f"{total_minutes}:{total_seconds:02d} minutes",
        description=generate_description(topic, sections, cta_text),
        chapters=youtube_chapters,
        segments=segments,
        thumbnail_idea=generate_thumbnail_idea(topic, raw_script["hook"]),
        end_screen_suggestion=generate_end_screen(topic),
        tags=generate_tags(topic, tone),
        model_used=model_used,
        cortex_version="1.0.0"
    )

    return production_script


def production_script_to_dict(ps: MediumProductionScript) -> dict:
    """Convert MediumProductionScript to a clean dictionary for output."""
    return {
        "title": ps.title,
        "topic": ps.topic,
        "tone": ps.tone,
        "total_duration": ps.total_duration,
        "description": ps.description,
        "youtube_chapters": ps.chapters,
        "segments": [
            {
                "segment_number": s.segment_number,
                "type": s.type,
                "title": s.title,
                "timestamp_start": s.timestamp_start,
                "timestamp_end": s.timestamp_end,
                "duration_seconds": s.duration_seconds,
                "teleprompter_text": s.teleprompter_text,
                "broll_suggestions": s.broll_suggestions,
                "key_points": s.key_points,
                "transition": s.transition
            }
            for s in ps.segments
        ],
        "thumbnail_idea": ps.thumbnail_idea,
        "end_screen_suggestion": ps.end_screen_suggestion,
        "tags": ps.tags,
        "metadata": {
            "model_used": ps.model_used,
            "cortex_version": ps.cortex_version
        }
    }
