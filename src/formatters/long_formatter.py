# src/formatters/long_formatter.py
# Cortex — Long Formatter
# Takes a raw long script and converts it into a
# production-ready podcast/long-form video script with
# pause markers, transition scripts, show notes, and TOC

from dataclasses import dataclass
from typing import List


# --- Data Structures ---

@dataclass
class PauseMarker:
    """Represents a natural pause point in the script."""
    position: str       # where in the chapter
    duration: str       # short (1-2s) / medium (3-5s) / long (5-10s)
    reason: str         # why to pause here


@dataclass
class Chapter:
    """Represents a single chapter in the long-form script."""
    chapter_number: int
    title: str
    timestamp_start: str
    timestamp_end: str
    duration_seconds: int
    word_count: int
    teleprompter_text: str
    pause_markers: List[PauseMarker]
    transition_in: str      # what to say entering this chapter
    transition_out: str     # what to say leaving this chapter
    key_takeaway: str       # one sentence summary
    visual_suggestions: List[str]


@dataclass
class ShowNotes:
    """Complete show notes for podcast platforms."""
    episode_title: str
    episode_summary: str
    table_of_contents: List[dict]
    key_takeaways: List[str]
    resources_section: str
    tags: List[str]


@dataclass
class LongProductionScript:
    """Complete production-ready breakdown for long-form content."""
    title: str
    topic: str
    tone: str
    total_duration: str
    word_count: int
    chapters: List[Chapter]
    show_notes: ShowNotes
    intro_script: str
    outro_script: str
    thumbnail_idea: str
    youtube_chapters: List[dict]
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
    """
    if isinstance(field, dict):
        return field.get("text", str(field))
    return str(field)


def estimate_duration(text: str, words_per_minute: int = 120) -> int:
    """
    Estimate speaking duration for long-form content.
    Long-form speakers pace slower at ~120 wpm for clarity.
    Returns duration in seconds.
    """
    word_count = len(text.split())
    minutes = word_count / words_per_minute
    return max(60, int(minutes * 60))  # minimum 1 minute per chapter


def count_words(text: str) -> int:
    """Count words in a text."""
    return len(text.split())


def generate_pause_markers(text: str) -> List[PauseMarker]:
    """
    Generate natural pause markers throughout the chapter.
    Pauses are placed at key transition points in the text.
    """
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
    markers = []
    total = len(sentences)

    if total == 0:
        return markers

    # Opening pause — after first impactful sentence
    markers.append(PauseMarker(
        position=f"After: '{' '.join(sentences[0].split()[:8])}...'",
        duration="medium (3-5s)",
        reason="Let the opening statement land before continuing"
    ))

    # Mid-chapter pause — at the halfway point
    if total > 4:
        mid = total // 2
        markers.append(PauseMarker(
            position=f"After: '{' '.join(sentences[mid].split()[:8])}...'",
            duration="short (1-2s)",
            reason="Natural breath point between main ideas"
        ))

    # Pre-takeaway pause — before the final key point
    if total > 2:
        markers.append(PauseMarker(
            position=f"After: '{' '.join(sentences[-2].split()[:8])}...'",
            duration="long (5-10s)",
            reason="Signal importance of upcoming key takeaway"
        ))

    return markers


def generate_transition_in(chapter_number: int, title: str,
                           prev_title: str = None) -> str:
    """Generate a natural transition script entering a chapter."""
    if chapter_number == 1:
        return (
            f"Alright, let's dive in. {title.replace('Chapter', '').strip()} "
            f"— this is where everything starts."
        )
    return (
        f"Now that we've covered {prev_title}, let's move on to "
        f"{title.replace('Chapter', '').strip()}. "
        f"This next part is crucial because it builds directly on what we just discussed."
    )


def generate_transition_out(title: str, next_title: str = None) -> str:
    """Generate a natural transition script leaving a chapter."""
    if next_title is None:
        return (
            "And that brings us to the end of our main content. "
            "Let's wrap everything up and look at the big picture."
        )
    clean_next = next_title.replace('Chapter', '').strip()
    return (
        f"So that covers {title.replace('Chapter', '').strip()}. "
        f"Coming up next — {clean_next}. "
        f"Take a breath, grab some water, and let's keep going."
    )


def extract_key_takeaway(content: str) -> str:
    """Extract the single most important takeaway from a chapter."""
    sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 20]
    if not sentences:
        return "Key insight from this chapter."
    # Use the last substantial sentence as it often contains the conclusion
    for sentence in reversed(sentences):
        if len(sentence.split()) > 8:
            return sentence + "."
    return sentences[0] + "."


def generate_visual_suggestions(title: str, content: str) -> List[str]:
    """Generate visual suggestions for long-form video content."""
    base = [
        f"Chapter title card: '{title}' — hold for 3 seconds",
        "Speaker on camera for personal connection moments",
        "Data visualizations or diagrams for complex concepts",
        "Text overlays for key statistics or quotes"
    ]
    keywords = {
        "history": ["timeline graphics", "archival imagery"],
        "business": ["business charts", "case study graphics"],
        "technology": ["screen recordings", "tech diagrams"],
        "science": ["scientific animations", "research graphics"],
        "startup": ["founder story visuals", "growth charts"],
        "team": ["team collaboration footage", "interview style shots"]
    }
    content_lower = (title + " " + content).lower()
    for keyword, extras in keywords.items():
        if keyword in content_lower:
            base.extend(extras)
            break

    return base[:5]


def generate_show_notes(topic: str, hook: str, chapters: List[Chapter],
                        cta: str, tone: str) -> ShowNotes:
    """Generate complete show notes for podcast platforms."""
    toc = [
        {
            "chapter": c.chapter_number,
            "title": c.title,
            "timestamp": c.timestamp_start,
            "duration": seconds_to_timestamp(c.duration_seconds)
        }
        for c in chapters
    ]

    key_takeaways = [c.key_takeaway for c in chapters]

    tags_by_tone = {
        "educational": ["education", "learning", "knowledge", "explained"],
        "motivational": ["motivation", "inspiration", "success", "mindset"],
        "storytelling": ["story", "narrative", "journey", "podcast"],
        "informative": ["facts", "breakdown", "deep dive", "analysis"],
        "funny": ["comedy", "entertainment", "humor", "fun"]
    }

    topic_tags = [w.lower() for w in topic.split() if len(w) > 3][:4]
    tone_tags = tags_by_tone.get(tone, ["content", "video"])
    all_tags = list(set(["podcast", "longform", "youtube"] + tone_tags + topic_tags))

    resources = (
        f"Resources mentioned in this episode:\n"
        f"• Search '{topic}' for further reading\n"
        f"• Check the description for recommended links\n"
        f"• Join our community to discuss this topic further"
    )

    return ShowNotes(
        episode_title=f"Cortex Long: {topic}",
        episode_summary=extract_text(hook),
        table_of_contents=toc,
        key_takeaways=key_takeaways,
        resources_section=resources,
        tags=all_tags
    )


def generate_intro_script(hook: str, intro: str, topic: str) -> str:
    """Generate a polished intro script combining hook and intro."""
    hook_text = extract_text(hook)
    intro_text = extract_text(intro)
    return (
        f"[INTRO MUSIC FADES]\n\n"
        f"{hook_text}\n\n"
        f"{intro_text}\n\n"
        f"[PAUSE 3 SECONDS — let the intro land]\n\n"
        f"Let's get into it."
    )


def generate_outro_script(topic: str, cta: str) -> str:
    """Generate a polished outro script."""
    cta_text = extract_text(cta)
    return (
        f"[OUTRO MUSIC STARTS SOFTLY]\n\n"
        f"And that's a wrap on {topic}.\n\n"
        f"{cta_text}\n\n"
        f"[PAUSE 2 SECONDS]\n\n"
        f"Thank you for spending this time with me today. "
        f"I'll see you in the next one.\n\n"
        f"[OUTRO MUSIC FADES UP — END SCREEN APPEARS]"
    )


def generate_thumbnail(topic: str, hook: str) -> str:
    """Generate thumbnail concept for long-form content."""
    hook_text = extract_text(hook)
    first_words = " ".join(hook_text.split()[:5]).upper()
    return (
        f"Long-form thumbnail style: Bold title text '{first_words}' "
        f"on a clean, professional background. "
        f"Creator face showing curiosity or expertise (not clickbait). "
        f"Subtle chapter number or episode indicator in corner. "
        f"Topic '{topic}' should be immediately clear from visuals alone."
    )


# --- Main Formatter Function ---

def format_long(raw_script: dict) -> LongProductionScript:
    """
    Main formatter function.
    Takes raw Cortex script output and returns a
    production-ready LongProductionScript.

    Args:
        raw_script: dict output from generate_script() with format='long'

    Returns:
        LongProductionScript with full chapter breakdown
    """

    # --- Validate input ---
    if raw_script.get("format") != "long":
        raise ValueError(
            f"Expected format 'long', got '{raw_script.get('format')}'. "
            f"Use the correct formatter for your script format."
        )

    required_keys = ["topic", "hook", "intro", "chapters", "conclusion", "cta"]
    for key in required_keys:
        if key not in raw_script:
            raise ValueError(f"Missing required field '{key}' in script.")

    # --- Extract fields defensively ---
    topic = raw_script["topic"]
    hook = raw_script["hook"]
    intro = raw_script["intro"]
    raw_chapters = raw_script["chapters"]
    conclusion = raw_script["conclusion"]
    cta = raw_script["cta"]
    tone = raw_script.get("metadata", {}).get("tone", "educational")
    model_used = raw_script.get("metadata", {}).get("model_used", "unknown")

    # --- Build chapters ---
    chapters = []
    current_second = 0
    youtube_chapters = []
    total_words = 0

    # Add intro duration
    intro_text = extract_text(intro)
    hook_text = extract_text(hook)
    intro_duration = estimate_duration(hook_text + " " + intro_text)
    youtube_chapters.append({
        "timestamp": seconds_to_timestamp(0),
        "title": "Introduction"
    })
    current_second += intro_duration

    # Build each chapter
    for i, raw_chapter in enumerate(raw_chapters):
        chapter_title = raw_chapter.get("title", f"Chapter {i+1}")
        chapter_content = raw_chapter.get("content", "")
        chapter_duration = estimate_duration(chapter_content)
        word_count = count_words(chapter_content)
        total_words += word_count

        # Get prev and next titles for transitions
        prev_title = raw_chapters[i-1].get("title") if i > 0 else None
        next_title = (raw_chapters[i+1].get("title")
                     if i < len(raw_chapters) - 1 else None)

        chapter = Chapter(
            chapter_number=i + 1,
            title=chapter_title,
            timestamp_start=seconds_to_timestamp(current_second),
            timestamp_end=seconds_to_timestamp(
                current_second + chapter_duration),
            duration_seconds=chapter_duration,
            word_count=word_count,
            teleprompter_text=chapter_content,
            pause_markers=generate_pause_markers(chapter_content),
            transition_in=generate_transition_in(i+1, chapter_title,
                                                  prev_title),
            transition_out=generate_transition_out(chapter_title,
                                                    next_title),
            key_takeaway=extract_key_takeaway(chapter_content),
            visual_suggestions=generate_visual_suggestions(
                chapter_title, chapter_content)
        )

        chapters.append(chapter)
        youtube_chapters.append({
            "timestamp": seconds_to_timestamp(current_second),
            "title": chapter_title
        })
        current_second += chapter_duration

    # Add conclusion and outro
    conclusion_text = extract_text(conclusion)
    conclusion_duration = estimate_duration(conclusion_text)
    youtube_chapters.append({
        "timestamp": seconds_to_timestamp(current_second),
        "title": "Conclusion"
    })
    current_second += conclusion_duration

    total_words += count_words(conclusion_text)

    # --- Build show notes ---
    show_notes = generate_show_notes(topic, hook, chapters, cta, tone)

    # --- Build final production script ---
    total_mins = current_second // 60
    total_secs = current_second % 60

    production_script = LongProductionScript(
        title=f"Cortex Long: {topic}",
        topic=topic,
        tone=tone,
        total_duration=f"{total_mins}:{total_secs:02d} minutes",
        word_count=total_words,
        chapters=chapters,
        show_notes=show_notes,
        intro_script=generate_intro_script(hook, intro, topic),
        outro_script=generate_outro_script(topic, cta),
        thumbnail_idea=generate_thumbnail(topic, hook),
        youtube_chapters=youtube_chapters,
        model_used=model_used,
        cortex_version="1.0.0"
    )

    return production_script


def production_script_to_dict(ps: LongProductionScript) -> dict:
    """Convert LongProductionScript to a clean dictionary for output."""
    return {
        "title": ps.title,
        "topic": ps.topic,
        "tone": ps.tone,
        "total_duration": ps.total_duration,
        "word_count": ps.word_count,
        "intro_script": ps.intro_script,
        "chapters": [
            {
                "chapter_number": c.chapter_number,
                "title": c.title,
                "timestamp_start": c.timestamp_start,
                "timestamp_end": c.timestamp_end,
                "duration_seconds": c.duration_seconds,
                "word_count": c.word_count,
                "teleprompter_text": c.teleprompter_text,
                "pause_markers": [
                    {
                        "position": p.position,
                        "duration": p.duration,
                        "reason": p.reason
                    }
                    for p in c.pause_markers
                ],
                "transition_in": c.transition_in,
                "transition_out": c.transition_out,
                "key_takeaway": c.key_takeaway,
                "visual_suggestions": c.visual_suggestions
            }
            for c in ps.chapters
        ],
        "outro_script": ps.outro_script,
        "youtube_chapters": ps.youtube_chapters,
        "show_notes": {
            "episode_title": ps.show_notes.episode_title,
            "episode_summary": ps.show_notes.episode_summary,
            "table_of_contents": ps.show_notes.table_of_contents,
            "key_takeaways": ps.show_notes.key_takeaways,
            "resources": ps.show_notes.resources_section,
            "tags": ps.show_notes.tags
        },
        "thumbnail_idea": ps.thumbnail_idea,
        "metadata": {
            "model_used": ps.model_used,
            "cortex_version": ps.cortex_version
        }
    }
