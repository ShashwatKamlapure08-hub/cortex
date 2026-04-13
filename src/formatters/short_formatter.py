# src/formatters/short_formatter.py
# Cortex — Short Formatter
# Takes a raw short script and converts it into a
# production-ready YouTube Shorts breakdown

from dataclasses import dataclass
from typing import List


# --- Data Structures ---

@dataclass
class Shot:
    """Represents a single visual shot in the video."""
    shot_number: int
    timestamp_start: str
    timestamp_end: str
    duration_seconds: int
    type: str           # hook / point / cta
    script_text: str
    visual_cue: str     # what should appear on screen
    subtitle: str       # exactly what appears as subtitle
    energy_level: str   # high / medium / low


@dataclass
class ShortProductionScript:
    """Complete production-ready breakdown for a YouTube Short."""
    title: str
    topic: str
    tone: str
    total_duration: str
    shots: List[Shot]
    caption: str
    hashtags: List[str]
    thumbnail_idea: str
    model_used: str
    cortex_version: str


# --- Helper Functions ---

def seconds_to_timestamp(seconds: int) -> str:
    """Convert seconds to MM:SS format."""
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"


def generate_visual_cue(text: str, shot_type: str) -> str:
    """Generate a visual cue suggestion based on the script text."""
    cues = {
        "hook": "Bold text on screen, fast zoom in, high energy background music starts",
        "point": "Text overlay with key words highlighted, relevant background footage or animation",
        "cta": "Subscribe button animation appears, creator face or channel logo shown"
    }
    return cues.get(shot_type, "Text overlay on relevant background footage")


def generate_subtitle(text: str, max_words: int = 8) -> str:
    """
    Create a punchy subtitle from script text.
    Subtitles in Shorts should be short and impactful.
    """
    words = text.split()
    if len(words) <= max_words:
        return text.upper()
    # Take most impactful words from start
    return " ".join(words[:max_words]).upper() + "..."


def generate_hashtags(topic: str, tone: str) -> List[str]:
    """Generate relevant hashtags for the Short."""
    base_tags = ["#Shorts", "#YouTubeShorts", "#LearnSomethingNew"]

    tone_tags = {
        "motivational": ["#Motivation", "#MindsetShift", "#LevelUp"],
        "educational": ["#DidYouKnow", "#LearnWithMe", "#Facts"],
        "funny": ["#Funny", "#Comedy", "#Humor"],
        "storytelling": ["#StoryTime", "#TrueStory", "#Narrative"],
        "informative": ["#Tips", "#HowTo", "#Explained"]
    }

    topic_words = topic.lower().split()
    topic_tags = [f"#{word.capitalize()}" for word in topic_words
                  if len(word) > 3][:3]

    selected_tone_tags = tone_tags.get(tone, ["#Content", "#Creator"])

    return base_tags + selected_tone_tags + topic_tags


def generate_caption(topic: str, hook: str, cta: str) -> str:
    """Generate a YouTube Shorts caption."""
    hook_preview = " ".join(hook.split()[:10])
    return f"{hook_preview}... \n\n{cta}\n\n"


def generate_thumbnail_idea(hook: str, topic: str) -> str:
    """Suggest a thumbnail concept based on the hook."""
    first_words = " ".join(hook.split()[:5]).upper()
    return (
        f"Bold text saying '{first_words}' on a high-contrast background. "
        f"Add a surprised or intense facial expression if using a person. "
        f"Keep it simple — one focal point related to '{topic}'."
    )


# --- Main Formatter Function ---

def format_short(raw_script: dict) -> ShortProductionScript:
    """
    Main formatter function.
    Takes raw Cortex script output and returns a
    production-ready ShortProductionScript.

    Args:
        raw_script: dict output from generate_script() with format='short'

    Returns:
        ShortProductionScript with full shot breakdown
    """

    # --- Validate input ---
    if raw_script.get("format") != "short":
        raise ValueError(
            f"Expected format 'short', got '{raw_script.get('format')}'. "
            f"Use the correct formatter for your script format."
        )

    required_keys = ["topic", "hook", "body", "cta"]
    for key in required_keys:
        if key not in raw_script:
            raise ValueError(f"Missing required field '{key}' in script.")

    topic = raw_script["topic"]
    hook = raw_script["hook"]
    body_points = raw_script["body"]
    cta = raw_script["cta"]
    tone = raw_script.get("metadata", {}).get("tone", "educational")
    model_used = raw_script.get("metadata", {}).get("model_used", "unknown")

    # --- Build shots ---
    shots = []
    current_second = 0

    # Shot 1 — Hook (0 to 5 seconds)
    hook_duration = 5
    shots.append(Shot(
        shot_number=1,
        timestamp_start=seconds_to_timestamp(current_second),
        timestamp_end=seconds_to_timestamp(current_second + hook_duration),
        duration_seconds=hook_duration,
        type="hook",
        script_text=hook,
        visual_cue=generate_visual_cue(hook, "hook"),
        subtitle=generate_subtitle(hook),
        energy_level="high"
    ))
    current_second += hook_duration

    # Shots 2 to N — Body points (evenly distributed in remaining time)
    # Reserve last 8 seconds for CTA
    remaining_for_body = 60 - hook_duration - 8
    point_duration = remaining_for_body // len(body_points)

    for i, point in enumerate(body_points):
        shots.append(Shot(
            shot_number=i + 2,
            timestamp_start=seconds_to_timestamp(current_second),
            timestamp_end=seconds_to_timestamp(current_second + point_duration),
            duration_seconds=point_duration,
            type="point",
            script_text=point,
            visual_cue=generate_visual_cue(point, "point"),
            subtitle=generate_subtitle(point),
            energy_level="medium"
        ))
        current_second += point_duration

    # Final Shot — CTA (last 8 seconds)
    shots.append(Shot(
        shot_number=len(shots) + 1,
        timestamp_start=seconds_to_timestamp(current_second),
        timestamp_end=seconds_to_timestamp(60),
        duration_seconds=8,
        type="cta",
        script_text=cta,
        visual_cue=generate_visual_cue(cta, "cta"),
        subtitle=generate_subtitle(cta),
        energy_level="high"
    ))

    # --- Build final production script ---
    production_script = ShortProductionScript(
        title=f"Cortex Short: {topic}",
        topic=topic,
        tone=tone,
        total_duration="60 seconds",
        shots=shots,
        caption=generate_caption(topic, hook, cta),
        hashtags=generate_hashtags(topic, tone),
        thumbnail_idea=generate_thumbnail_idea(hook, topic),
        model_used=model_used,
        cortex_version="1.0.0"
    )

    return production_script


def production_script_to_dict(ps: ShortProductionScript) -> dict:
    """Convert ShortProductionScript to a clean dictionary for output."""
    return {
        "title": ps.title,
        "topic": ps.topic,
        "tone": ps.tone,
        "total_duration": ps.total_duration,
        "shots": [
            {
                "shot_number": s.shot_number,
                "timestamp_start": s.timestamp_start,
                "timestamp_end": s.timestamp_end,
                "duration_seconds": s.duration_seconds,
                "type": s.type,
                "script_text": s.script_text,
                "visual_cue": s.visual_cue,
                "subtitle": s.subtitle,
                "energy_level": s.energy_level
            }
            for s in ps.shots
        ],
        "caption": ps.caption,
        "hashtags": ps.hashtags,
        "thumbnail_idea": ps.thumbnail_idea,
        "metadata": {
            "model_used": ps.model_used,
            "cortex_version": ps.cortex_version
        }
    }
