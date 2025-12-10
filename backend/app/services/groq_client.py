# backend/app/services/groq_client.py
import os
import requests
from app.config import GROQ_API_KEY

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def refine_prompt(original_prompt: str, duration_seconds: int) -> str:
    """
    Call Groq LLM to expand/refine video prompt.
    """
    if not GROQ_API_KEY:
        return original_prompt

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    system_prompt = (
        "You are an AI director. Expand the user's idea into a precise video prompt "
        "for a generative video model. Mention scene, camera, lighting, style, and motion. "
        f"Target duration: ~{duration_seconds} seconds. Keep it concise (1-2 sentences)."
    )

    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": original_prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 300,
    }

    try:
        resp = requests.post(GROQ_API_URL, headers=headers, json=data, timeout=20)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return content.strip()
    except Exception:
        return original_prompt
