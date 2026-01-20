from groq import Groq
from prompts import SYSTEM_PROMPT
import os, json

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "llama-3.1-8b-instant"

def ask_llm(user_text: str) -> dict:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ]
    )

    raw = response.choices[0].message.content
    # Try to parse the LLM output as JSON. If the model returns extra text
    # before/after the JSON, attempt to extract the first balanced JSON object.
    try:
        return json.loads(raw)
    except Exception:
        # find first balanced JSON object
        def extract_json(text: str) -> str | None:
            start = text.find('{')
            if start == -1:
                return None
            depth = 0
            for i, ch in enumerate(text[start:], start=start):
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        return text[start:i+1]
            return None

        jtext = extract_json(raw)
        if jtext:
            try:
                return json.loads(jtext)
            except Exception:
                pass

    # Fallback: echo the raw text into display/speak fields to avoid crashing.
    # The assistant will still function but show the raw response.
    print("[llm] Warning: failed to parse JSON from model output; using fallback.")
    return {
        "address": "none",
        "emotion": "calm",
        "speak": raw.strip(),
        "display": raw.strip(),
        "action": {"type": "none", "command": ""}
    }
