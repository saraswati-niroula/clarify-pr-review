import os
import google.generativeai as genai


def configure_gemini(model_name: str = "gemini-1.5-flash"):
    """
    Returns a GenerativeModel instance for the given Gemini model.
    Requires GEMINI_API_KEY env var.
    """
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("Missing GEMINI_API_KEY")
    genai.configure(api_key=key)
    return genai.GenerativeModel(model_name)
