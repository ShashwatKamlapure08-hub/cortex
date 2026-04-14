# src/api/routes.py
# Cortex — API Routes
# All the endpoints Cortex exposes to the world

from fastapi import APIRouter, HTTPException
from src.api.models import ScriptRequest, ScriptResponse, ErrorResponse
from src.engine.script_engine import generate_script
from src.formatters.short_formatter import (
    format_short,
    production_script_to_dict as short_to_dict
)
from src.formatters.medium_formatter import (
    format_medium,
    production_script_to_dict as medium_to_dict
)
from src.formatters.long_formatter import (
    format_long,
    production_script_to_dict as long_to_dict
)

router = APIRouter()

FORMATTER_MAP = {
    "short": (format_short, short_to_dict),
    "medium": (format_medium, medium_to_dict),
    "long": (format_long, long_to_dict)
}


def apply_formatter(raw_script: dict, format: str) -> dict:
    """Apply the appropriate formatter to a raw script."""
    if format not in FORMATTER_MAP:
        raise ValueError(f"No formatter found for format: {format}")

    formatter_fn, to_dict_fn = FORMATTER_MAP[format]
    production = formatter_fn(raw_script)
    return to_dict_fn(production)


def generate_with_retry(topic: str, format: str,
                         tone: str, max_retries: int = 3) -> dict:
    """
    Generate a script with retry logic.
    If the model returns a parse error, retry up to max_retries times.
    This fixes the occasional JSON parse errors we saw in testing.
    """
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            result = generate_script(topic=topic, format=format, tone=tone)

            # Check if we got a parse error
            if "parse_error" in result:
                print(f"⚠️  Parse error on attempt {attempt}, retrying...")
                last_error = result.get("parse_error")
                continue

            return result

        except Exception as e:
            last_error = str(e)
            print(f"⚠️  Attempt {attempt} failed: {e}")
            if attempt == max_retries:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed after {max_retries} attempts: {last_error}"
                )

    raise HTTPException(
        status_code=500,
        detail=f"Script generation failed after retries: {last_error}"
    )


# --- Health Check ---

@router.get("/health")
def health_check():
    """Check if Cortex API is running."""
    return {
        "status": "healthy",
        "service": "Cortex Script Engine",
        "version": "1.0.0"
    }


# --- Main Script Generation Endpoint ---

@router.post(
    "/generate",
    response_model=ScriptResponse,
    summary="Generate a script",
    description="Generate a production-ready script for any format and tone."
)
def generate(request: ScriptRequest):
    """
    Main endpoint to generate a Cortex script.

    - **topic**: What the video is about
    - **format**: short / medium / long
    - **tone**: educational / motivational / funny / storytelling / informative
    - **apply_formatter**: Whether to apply production formatting
    """
    try:
        # Generate with retry logic
        raw_script = generate_with_retry(
            topic=request.topic,
            format=request.format.value,
            tone=request.tone.value
        )

        model_used = raw_script.get(
            "metadata", {}
        ).get("model_used", "unknown")

        # Apply formatter if requested
        if request.apply_formatter:
            final_script = apply_formatter(
                raw_script, request.format.value
            )
            formatted = True
        else:
            final_script = raw_script
            formatted = False

        return ScriptResponse(
            success=True,
            topic=request.topic,
            format=request.format.value,
            tone=request.tone.value,
            model_used=model_used,
            formatted=formatted,
            script=final_script
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Quick Endpoints for Each Format ---

@router.post("/generate/short", summary="Generate a Short script")
def generate_short(topic: str, tone: str = "motivational"):
    """Quick endpoint specifically for YouTube Shorts."""
    try:
        raw = generate_with_retry(topic=topic, format="short", tone=tone)
        formatted = apply_formatter(raw, "short")
        return {"success": True, "script": formatted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/medium", summary="Generate a Medium script")
def generate_medium(topic: str, tone: str = "educational"):
    """Quick endpoint specifically for medium YouTube videos."""
    try:
        raw = generate_with_retry(topic=topic, format="medium", tone=tone)
        formatted = apply_formatter(raw, "medium")
        return {"success": True, "script": formatted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/long", summary="Generate a Long script")
def generate_long(topic: str, tone: str = "storytelling"):
    """Quick endpoint specifically for long-form content and podcasts."""
    try:
        raw = generate_with_retry(topic=topic, format="long", tone=tone)
        formatted = apply_formatter(raw, "long")
        return {"success": True, "script": formatted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Formats Info Endpoint ---

@router.get("/formats", summary="List available formats")
def list_formats():
    """Returns all available script formats and tones."""
    return {
        "formats": {
            "short": "60-second YouTube Shorts script with shot breakdown",
            "medium": "8-10 minute YouTube video with teleprompter and chapters",
            "long": "20-30 minute podcast/long-form with show notes"
        },
        "tones": [
            "educational",
            "motivational",
            "funny",
            "storytelling",
            "informative"
        ]
    }
