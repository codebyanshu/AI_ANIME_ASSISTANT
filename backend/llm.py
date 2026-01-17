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
    return json.loads(raw)
