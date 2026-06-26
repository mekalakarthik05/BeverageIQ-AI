import ollama
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import OLLAMA_MODEL

def generate_business_explanation(prompt: str) -> str:
    """
    Sends the prompt to the local Ollama instance and returns the generated text.
    Handles connection errors gracefully.
    """
    try:
        response = ollama.generate(
            model=OLLAMA_MODEL,
            prompt=prompt,
            options={
                "temperature": 0.2 # Low temperature to prevent hallucination
            }
        )
        return response['response']
    except Exception as e:
        return f"**Error generating explanation:** Could not connect to Ollama. Please ensure Ollama is running and the model '{OLLAMA_MODEL}' is installed.\n\nDetails: {e}"
