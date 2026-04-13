# src/engine/script_engine.py
# Cortex — Core Script Engine
# Generates structured scripts for any format

import json
from src.models.model_manager import generate


# --- Prompt Templates ---

SHORTS_PROMPT = """
You are Cortex, an expert YouTube Shorts scriptwriter.
Write a 60-second script about: {topic}
Tone: {tone}

Structure your response EXACTLY in this JSON format:
{{
    "format": "short",
    "topic": "{topic}",
    "hook": "Opening line that grabs attention in 5 seconds",
    "body": ["Point 1", "Point 2", "Point 3"],
    "cta": "Call to action at the end",
    "estimated_duration": "60 seconds"
}}

Return ONLY the JSON. No explanation. No extra text.
"""

MEDIUM_PROMPT = """
You are Cortex, an expert YouTube scriptwriter.
Write a detailed 8-10 minute video script about: {topic}
Tone: {tone}

Structure your response EXACTLY in this JSON format:
{{
    "format": "medium",
    "topic": "{topic}",
    "hook": "Compelling opening that hooks viewer in 30 seconds",
    "intro": "Brief introduction setting up the video",
    "sections": [
        {{"title": "Section 1 title", "content": "Detailed content for this section"}},
        {{"title": "Section 2 title", "content": "Detailed content for this section"}},
        {{"title": "Section 3 title", "content": "Detailed content for this section"}}
    ],
    "conclusion": "Wrap up and key takeaways",
    "cta": "Call to action",
    "estimated_duration": "8-10 minutes"
}}

Return ONLY the JSON. No explanation. No extra text.
"""

LONG_PROMPT = """
You are Cortex, an expert content writer for long-form videos and podcasts.
Write a comprehensive script about: {topic}
Tone: {tone}

Structure your response EXACTLY in this JSON format:
{{
    "format": "long",
    "topic": "{topic}",
    "hook": "Strong opening narrative",
    "intro": "Full introduction with context setting",
    "chapters": [
        {{"chapter": 1, "title": "Chapter title", "content": "Detailed chapter content", "duration": "5 minutes"}},
        {{"chapter": 2, "title": "Chapter title", "content": "Detailed chapter content", "duration": "5 minutes"}},
        {{"chapter": 3, "title": "Chapter title", "content": "Detailed chapter content", "duration": "5 minutes"}},
        {{"chapter": 4, "title": "Chapter title", "content": "Detailed chapter content", "duration": "5 minutes"}}
    ],
    "conclusion": "Full conclusion with key takeaways",
    "cta": "Call to action",
    "estimated_duration": "20-30 minutes"
}}

Return ONLY the JSON. No explanation. No extra text.
"""

PROMPT_MAP = {
    "short": SHORTS_PROMPT,
    "medium": MEDIUM_PROMPT,
    "long": LONG_PROMPT
}

VALID_TONES = ["educational", "motivational", "funny", "storytelling", "informative"]
VALID_FORMATS = ["short", "medium", "long"]


def generate_script(topic: str, format: str = "short", tone: str = "educational") -> dict:
    """
    Main function to generate a Cortex script.
    
    Args:
        topic: What the video is about
        format: 'short', 'medium', or 'long'
        tone: 'educational', 'motivational', 'funny', 'storytelling', 'informative'
    
    Returns:
        dict with script data and metadata
    """
    
    # --- Validate inputs ---
    if format not in VALID_FORMATS:
        raise ValueError(f"Invalid format. Choose from: {VALID_FORMATS}")
    
    if tone not in VALID_TONES:
        raise ValueError(f"Invalid tone. Choose from: {VALID_TONES}")
    
    if not topic or len(topic.strip()) < 3:
        raise ValueError("Topic must be at least 3 characters long.")
    
    print(f"\n🧠 Cortex is generating a {format} script about '{topic}'...")
    print(f"🎭 Tone: {tone}")
    
    # --- Build prompt ---
    prompt = PROMPT_MAP[format].format(topic=topic, tone=tone)
    
    # --- Generate using model manager ---
    model_result = generate(prompt)
    raw_response = model_result["response"]
    model_used = model_result["model_used"]
    
    # --- Parse JSON response ---
    try:
        # Clean response in case model adds extra text
        clean = raw_response.strip()
        if "```json" in clean:
            clean = clean.split("```json")[1].split("```")[0].strip()
        elif "```" in clean:
            clean = clean.split("```")[1].split("```")[0].strip()
        
        script_data = json.loads(clean)
        
    except json.JSONDecodeError:
        # If JSON parsing fails, return raw response
        script_data = {
            "format": format,
            "topic": topic,
            "raw_output": raw_response,
            "parse_error": "Could not parse structured output"
        }
    
    # --- Add metadata ---
    script_data["metadata"] = {
        "model_used": model_used,
        "tone": tone,
        "cortex_version": "1.0.0"
    }
    
    print(f"✅ Script generated using {model_used}!")
    return script_data
