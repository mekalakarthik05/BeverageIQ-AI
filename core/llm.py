import ollama
import google.generativeai as genai
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import LLM_PROVIDER, OLLAMA_MODEL, OLLAMA_API_URL, GEMINI_API_KEY

def generate_business_explanation(prompt: str, provider_override: str = None) -> str:
    """
    Sends the prompt to the configured LLM provider (Ollama or Gemini) and returns the generated text.
    Handles connection errors gracefully without auto-fallback.
    """
    provider = provider_override if provider_override else LLM_PROVIDER

    def call_ollama():
        client = ollama.Client(host=OLLAMA_API_URL)
        response = client.generate(
            model=OLLAMA_MODEL,
            prompt=prompt,
            options={"temperature": 0.2}
        )
        return response['response']

    def call_gemini():
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set.")
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.2)
        )
        return response.text

    if provider == "ollama":
        try:
            return call_ollama()
        except Exception:
            return "__OLLAMA_UNAVAILABLE__"
                
    elif provider == "gemini":
        try:
            return call_gemini()
        except Exception as e:
            return f"**Error generating explanation:** Gemini API failed.\n\nDetails: {e}"
    else:
        return f"**Error:** Unknown LLM_PROVIDER '{provider}' specified in configuration."
