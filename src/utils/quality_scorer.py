# src/utils/quality_scorer.py
# Cortex — Quality Scorer
# Evaluates every script across 5 dimensions and
# gives an overall score out of 100

from dataclasses import dataclass
from typing import List


# --- Data Structures ---

@dataclass
class DimensionScore:
    """Score for a single quality dimension."""
    name: str
    score: int          # 0-20
    max_score: int      # always 20
    feedback: str
    suggestions: List[str]


@dataclass
class QualityReport:
    """Complete quality report for a script."""
    overall_score: int      # 0-100
    grade: str              # A / B / C / D / F
    passed: bool            # True if score >= 70
    dimensions: List[DimensionScore]
    strengths: List[str]
    improvements: List[str]
    regenerate: bool        # True if score < 50


# --- Scoring Helpers ---

def grade_from_score(score: int) -> str:
    """Convert numeric score to letter grade."""
    if score >= 90: return "A"
    if score >= 80: return "B"
    if score >= 70: return "C"
    if score >= 60: return "D"
    return "F"


def extract_text(field) -> str:
    """Safely extract text from string or dict field."""
    if isinstance(field, dict):
        return field.get("text", str(field))
    return str(field) if field else ""


# --- Dimension 1: Hook Strength ---

def score_hook(hook: str) -> DimensionScore:
    """
    Score the opening hook out of 20.
    A great hook grabs attention in the first 5 seconds.
    """
    score = 0
    feedback_points = []
    suggestions = []
    hook_lower = hook.lower()

    # Length check — hooks should be punchy, not too long or too short
    word_count = len(hook.split())
    if 8 <= word_count <= 25:
        score += 5
        feedback_points.append("Good hook length")
    elif word_count < 8:
        suggestions.append("Hook is too short — add more impact")
    else:
        suggestions.append("Hook is too long — trim it to under 25 words")

    # Question hook — questions engage viewers immediately
    if "?" in hook:
        score += 4
        feedback_points.append("Uses a question to engage viewer")
    else:
        suggestions.append("Consider opening with a question to hook the viewer")

    # Power words that drive engagement
    power_words = [
        "imagine", "secret", "discover", "never", "always",
        "mistake", "truth", "stop", "start", "transform",
        "unlock", "reveal", "shocking", "proven", "fastest"
    ]
    found_power = [w for w in power_words if w in hook_lower]
    if found_power:
        score += 4
        feedback_points.append(f"Uses power words: {', '.join(found_power)}")
    else:
        suggestions.append("Add power words like 'imagine', 'discover', or 'unlock'")

    # Emotional trigger — hooks that create emotion retain viewers
    emotion_words = [
        "tired", "struggling", "afraid", "excited", "frustrated",
        "overwhelmed", "motivated", "inspired", "stuck", "lost",
        "dream", "fear", "love", "hate", "feel"
    ]
    found_emotion = [w for w in emotion_words if w in hook_lower]
    if found_emotion:
        score += 4
        feedback_points.append("Creates emotional connection")
    else:
        suggestions.append("Add emotional language to connect with your audience")

    # Specificity — specific hooks outperform vague ones
    specific_indicators = [
        any(char.isdigit() for char in hook),  # contains numbers
        "%" in hook,
        "minute" in hook_lower,
        "second" in hook_lower,
        "step" in hook_lower
    ]
    if any(specific_indicators):
        score += 3
        feedback_points.append("Contains specific detail or number")
    else:
        suggestions.append("Add a specific number or timeframe for more impact")

    feedback = " | ".join(feedback_points) if feedback_points else "Hook needs improvement"
    return DimensionScore(
        name="Hook Strength",
        score=min(score, 20),
        max_score=20,
        feedback=feedback,
        suggestions=suggestions
    )


# --- Dimension 2: Pacing ---

def score_pacing(script: dict) -> DimensionScore:
    """
    Score the pacing out of 20.
    Good pacing means content is evenly distributed and timed well.
    """
    score = 0
    feedback_points = []
    suggestions = []
    format_type = script.get("format", "short")

    if format_type == "short":
        body = script.get("body", [])

        # Shorts should have 2-4 body points
        if 2 <= len(body) <= 4:
            score += 8
            feedback_points.append(f"Good number of points ({len(body)}) for a Short")
        elif len(body) < 2:
            score += 3
            suggestions.append("Add more body points — aim for 3 clear points")
        else:
            score += 4
            suggestions.append("Too many points for a 60-second Short — reduce to 3")

        # Check individual point lengths
        ideal_points = [p for p in body if 8 <= len(p.split()) <= 30]
        if len(ideal_points) == len(body):
            score += 7
            feedback_points.append("Each point is well-paced")
        else:
            score += 3
            suggestions.append("Some points are too long or too short for a Short")

        # CTA should be punchy
        cta = script.get("cta", "")
        if len(cta.split()) <= 20:
            score += 5
            feedback_points.append("CTA is concise and punchy")
        else:
            score += 2
            suggestions.append("Shorten your CTA — under 20 words works best for Shorts")

    elif format_type == "medium":
        sections = script.get("sections", [])

        # Medium videos should have 2-4 sections
        if 2 <= len(sections) <= 4:
            score += 8
            feedback_points.append(f"Good section count ({len(sections)}) for a medium video")
        else:
            score += 3
            suggestions.append("Aim for 3 sections in a medium video for best pacing")

        # Each section should have substantial content
        good_sections = [
            s for s in sections
            if len(s.get("content", "").split()) >= 50
        ]
        if len(good_sections) == len(sections):
            score += 7
            feedback_points.append("All sections have sufficient depth")
        else:
            score += 3
            suggestions.append("Some sections are too thin — add more depth")

        score += 5
        feedback_points.append("Medium format structure detected")

    elif format_type == "long":
        chapters = script.get("chapters", [])

        # Long form should have 3-6 chapters
        if 3 <= len(chapters) <= 6:
            score += 10
            feedback_points.append(f"Good chapter count ({len(chapters)}) for long-form")
        else:
            score += 5
            suggestions.append("Aim for 4 chapters for optimal long-form pacing")

        # Chapters should be detailed
        detailed = [
            c for c in chapters
            if len(c.get("content", "").split()) >= 60
        ]
        if len(detailed) == len(chapters):
            score += 10
            feedback_points.append("All chapters have strong depth")
        else:
            score += 5
            suggestions.append("Some chapters need more detail")

    feedback = " | ".join(feedback_points) if feedback_points else "Pacing needs work"
    return DimensionScore(
        name="Pacing",
        score=min(score, 20),
        max_score=20,
        feedback=feedback,
        suggestions=suggestions
    )


# --- Dimension 3: Clarity ---

def score_clarity(script: dict) -> DimensionScore:
    """
    Score the clarity out of 20.
    Clear scripts use simple language and avoid jargon.
    """
    score = 0
    feedback_points = []
    suggestions = []

    # Collect all text from the script
    all_text = ""
    all_text += extract_text(script.get("hook", "")) + " "
    all_text += extract_text(script.get("intro", "")) + " "

    if script.get("format") == "short":
        for point in script.get("body", []):
            all_text += point + " "
    elif script.get("format") == "medium":
        for section in script.get("sections", []):
            all_text += section.get("content", "") + " "
    elif script.get("format") == "long":
        for chapter in script.get("chapters", []):
            all_text += chapter.get("content", "") + " "

    all_text += extract_text(script.get("conclusion", "")) + " "
    all_text += extract_text(script.get("cta", ""))

    words = all_text.split()
    if not words:
        return DimensionScore(
            name="Clarity",
            score=0,
            max_score=20,
            feedback="No content to evaluate",
            suggestions=["Add content to all script fields"]
        )

    # Average word length — shorter = clearer
    avg_word_length = sum(len(w) for w in words) / len(words)
    if avg_word_length <= 5:
        score += 7
        feedback_points.append("Uses simple, accessible language")
    elif avg_word_length <= 6.5:
        score += 4
        feedback_points.append("Language is mostly clear")
        suggestions.append("Simplify some longer words for better audience retention")
    else:
        score += 1
        suggestions.append("Use simpler language — write as you speak")

    # Sentence variety — mix of short and long sentences
    sentences = [s.strip() for s in all_text.split('.') if len(s.strip()) > 5]
    if sentences:
        lengths = [len(s.split()) for s in sentences]
        avg_len = sum(lengths) / len(lengths)
        if 10 <= avg_len <= 20:
            score += 6
            feedback_points.append("Good sentence length for spoken content")
        elif avg_len < 10:
            score += 3
            suggestions.append("Some sentences are too short — add more detail")
        else:
            score += 3
            suggestions.append("Sentences are too long for spoken delivery — break them up")

    # Transition words — help viewer follow along
    transition_words = [
        "first", "second", "third", "next", "then", "finally",
        "however", "because", "therefore", "so", "but", "also",
        "additionally", "in conclusion", "to summarize"
    ]
    found_transitions = [w for w in transition_words if w in all_text.lower()]
    if len(found_transitions) >= 3:
        score += 4
        feedback_points.append("Good use of transition words")
    elif len(found_transitions) >= 1:
        score += 2
        suggestions.append("Add more transition words to guide your audience")
    else:
        suggestions.append("Use transitions like 'first', 'next', 'finally' for clarity")

    # Personal pronouns — direct address improves clarity
    pronouns = ["you", "your", "we", "our"]
    found_pronouns = [p for p in pronouns if p in all_text.lower()]
    if found_pronouns:
        score += 3
        feedback_points.append("Directly addresses the audience")
    else:
        suggestions.append("Use 'you' and 'your' to speak directly to your audience")

    feedback = " | ".join(feedback_points) if feedback_points else "Clarity needs improvement"
    return DimensionScore(
        name="Clarity",
        score=min(score, 20),
        max_score=20,
        feedback=feedback,
        suggestions=suggestions
    )


# --- Dimension 4: Engagement Potential ---

def score_engagement(script: dict) -> DimensionScore:
    """
    Score the engagement potential out of 20.
    High engagement scripts keep viewers watching till the end.
    """
    score = 0
    feedback_points = []
    suggestions = []

    all_text = ""
    if script.get("format") == "short":
        all_text = " ".join([
            extract_text(script.get("hook", "")),
            " ".join(script.get("body", [])),
            extract_text(script.get("cta", ""))
        ])
    elif script.get("format") == "medium":
        sections_text = " ".join([
            s.get("content", "") for s in script.get("sections", [])
        ])
        all_text = " ".join([
            extract_text(script.get("hook", "")),
            extract_text(script.get("intro", "")),
            sections_text,
            extract_text(script.get("conclusion", ""))
        ])
    elif script.get("format") == "long":
        chapters_text = " ".join([
            c.get("content", "") for c in script.get("chapters", [])
        ])
        all_text = " ".join([
            extract_text(script.get("hook", "")),
            extract_text(script.get("intro", "")),
            chapters_text,
            extract_text(script.get("conclusion", ""))
        ])

    all_lower = all_text.lower()

    # Storytelling elements
    story_words = [
        "imagine", "story", "once", "journey", "remember",
        "picture this", "let me tell", "i was", "we were"
    ]
    found_story = [w for w in story_words if w in all_lower]
    if found_story:
        score += 5
        feedback_points.append("Contains storytelling elements")
    else:
        suggestions.append("Add a brief story or anecdote to boost engagement")

    # Curiosity gaps — phrases that make viewers want to keep watching
    curiosity_phrases = [
        "but here's", "the secret", "what most people", "you won't believe",
        "the surprising", "here's why", "the real reason", "what if",
        "the truth about", "most people don't"
    ]
    found_curiosity = [p for p in curiosity_phrases if p in all_lower]
    if found_curiosity:
        score += 5
        feedback_points.append("Uses curiosity gaps effectively")
    else:
        suggestions.append(
            "Add phrases like 'here's why' or 'most people don't know' "
            "to create curiosity"
        )

    # Social proof or data points
    has_numbers = any(char.isdigit() for char in all_text)
    social_proof = ["studies show", "research", "according to", "%", "million", "billion"]
    found_proof = [p for p in social_proof if p in all_lower]
    if has_numbers or found_proof:
        score += 5
        feedback_points.append("Includes data or social proof")
    else:
        suggestions.append("Add statistics or research to build credibility")

    # Actionable content
    action_words = [
        "try", "start", "do", "make", "build", "create",
        "take", "use", "apply", "implement", "practice"
    ]
    found_actions = [w for w in action_words if w in all_lower]
    if len(found_actions) >= 3:
        score += 5
        feedback_points.append("Highly actionable content")
    elif len(found_actions) >= 1:
        score += 3
        suggestions.append("Make content more actionable with specific steps")
    else:
        suggestions.append("Add actionable steps the viewer can take immediately")

    feedback = " | ".join(feedback_points) if feedback_points else "Engagement needs work"
    return DimensionScore(
        name="Engagement Potential",
        score=min(score, 20),
        max_score=20,
        feedback=feedback,
        suggestions=suggestions
    )


# --- Dimension 5: CTA Effectiveness ---

def score_cta(cta: str) -> DimensionScore:
    """
    Score the call to action out of 20.
    A great CTA tells viewers exactly what to do next.
    """
    score = 0
    feedback_points = []
    suggestions = []
    cta_lower = cta.lower()

    # CTA should exist and be meaningful
    if not cta or len(cta.strip()) < 5:
        return DimensionScore(
            name="CTA Effectiveness",
            score=0,
            max_score=20,
            feedback="No CTA found",
            suggestions=["Add a clear call to action at the end of your script"]
        )

    # Action verbs in CTA
    action_verbs = [
        "subscribe", "follow", "comment", "share", "like",
        "download", "join", "click", "visit", "check out",
        "start", "try", "get", "grab", "learn"
    ]
    found_actions = [v for v in action_verbs if v in cta_lower]
    if len(found_actions) >= 2:
        score += 8
        feedback_points.append(f"Strong action verbs: {', '.join(found_actions[:3])}")
    elif len(found_actions) == 1:
        score += 4
        feedback_points.append(f"Has action verb: {found_actions[0]}")
        suggestions.append("Add a second action — e.g., 'subscribe AND comment below'")
    else:
        suggestions.append(
            "Add action verbs like 'subscribe', 'comment', or 'share'"
        )

    # Urgency or reason to act now
    urgency_words = [
        "now", "today", "right now", "don't wait",
        "immediately", "this week", "start today"
    ]
    found_urgency = [w for w in urgency_words if w in cta_lower]
    if found_urgency:
        score += 5
        feedback_points.append("Creates urgency")
    else:
        suggestions.append("Add urgency with words like 'today' or 'right now'")

    # Benefit-driven CTA
    benefit_words = [
        "because", "so you can", "to help", "and get",
        "to learn", "for more", "to discover", "and unlock"
    ]
    found_benefits = [b for b in benefit_words if b in cta_lower]
    if found_benefits:
        score += 4
        feedback_points.append("Benefit-driven CTA")
    else:
        suggestions.append("Explain WHY they should act — add a benefit")

    # CTA length — should be concise
    word_count = len(cta.split())
    if word_count <= 30:
        score += 3
        feedback_points.append("CTA is concise and clear")
    else:
        score += 1
        suggestions.append("Shorten your CTA — under 30 words is ideal")

    feedback = " | ".join(feedback_points) if feedback_points else "CTA needs improvement"
    return DimensionScore(
        name="CTA Effectiveness",
        score=min(score, 20),
        max_score=20,
        feedback=feedback,
        suggestions=suggestions
    )


# --- Main Scorer Function ---

def score_script(script: dict) -> QualityReport:
    """
    Main scoring function.
    Evaluates a raw script across all 5 dimensions.

    Args:
        script: Raw script dict from generate_script()

    Returns:
        QualityReport with scores, feedback, and suggestions
    """

    # Extract hook and CTA defensively
    hook = extract_text(script.get("hook", ""))
    cta = extract_text(script.get("cta", ""))

    # Score all 5 dimensions
    hook_score = score_hook(hook)
    pacing_score = score_pacing(script)
    clarity_score = score_clarity(script)
    engagement_score = score_engagement(script)
    cta_score = score_cta(cta)

    dimensions = [
        hook_score,
        pacing_score,
        clarity_score,
        engagement_score,
        cta_score
    ]

    # Calculate overall score
    overall = sum(d.score for d in dimensions)
    grade = grade_from_score(overall)
    passed = overall >= 70
    regenerate = overall < 50

    # Collect strengths and improvements
    strengths = [
        f"{d.name}: {d.feedback}"
        for d in dimensions if d.score >= 15
    ]
    improvements = []
    for d in dimensions:
        if d.score < 15:
            improvements.extend(d.suggestions[:2])

    return QualityReport(
        overall_score=overall,
        grade=grade,
        passed=passed,
        dimensions=dimensions,
        strengths=strengths,
        improvements=improvements,
        regenerate=regenerate
    )


def quality_report_to_dict(report: QualityReport) -> dict:
    """Convert QualityReport to a clean dictionary."""
    return {
        "overall_score": report.overall_score,
        "grade": report.grade,
        "passed": report.passed,
        "regenerate_recommended": report.regenerate,
        "dimensions": [
            {
                "name": d.name,
                "score": d.score,
                "max_score": d.max_score,
                "percentage": round((d.score / d.max_score) * 100),
                "feedback": d.feedback,
                "suggestions": d.suggestions
            }
            for d in report.dimensions
        ],
        "strengths": report.strengths,
        "improvements": report.improvements
    }
