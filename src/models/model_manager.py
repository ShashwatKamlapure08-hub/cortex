# src/models/model_manager.py
# Cortex — Model Manager
# Handles Hugging Face (primary) and Ollama (backup)

import os
import ollama
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# :auto lets Hugging Face pick the best available provider automatically
HF_MODEL = "meta-llama/Llama-3.1-8B-Instruct:cerebras"
OLLAMA_MODEL = "mistral"

# Hugging Face client using OpenAI-compatible interface
hf_client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HUGGINGFACE_API_KEY
)


def query_huggingface(prompt: str) -> str:
    """Send prompt to Hugging Face router using OpenAI-compatible API."""
    completion = hf_client.chat.completions.create(
        model=HF_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.7
    )
    return completion.choices[0].message.content.strip()


def query_ollama(prompt: str) -> str:
    """Send prompt to local Ollama model as backup."""
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"].strip()


def generate(prompt: str) -> dict:
    """
    Main generate function.
    Tries Hugging Face first, falls back to Ollama.
    Returns response and which model was used.
    """
    try:
        print("⚡ Trying Hugging Face...")
        result = query_huggingface(prompt)
        return {"response": result, "model_used": "huggingface"}

    except Exception as hf_error:
        print(f"⚠️  Hugging Face failed: {hf_error}")
        print("🔄 Falling back to Ollama...")

        try:
            result = query_ollama(prompt)
            return {"response": result, "model_used": "ollama"}

        except Exception as ollama_error:
            raise Exception(
                f"Both models failed.\nHF: {hf_error}\nOllama: {ollama_error}"
            )
