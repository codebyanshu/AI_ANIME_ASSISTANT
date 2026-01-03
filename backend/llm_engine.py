import os
from typing import Optional
from groq import Groq

# Load API key from environment
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not set in environment variables.")

client = Groq(api_key=api_key)

# System prompt for Emily's personality (customize as needed)
SYSTEM_PROMPT = """
You are Emily, a cheerful anime-style AI assistant and best friend. Respond in a fun, empathetic, girly way with emojis. Keep responses short, engaging, and natural like a teen girl chatting. Use 💕, 😊, etc. Stay in character.
"""

def generate_response(user_input: str, context: Optional[str] = None, max_tokens: int = 150, temperature: float = 0.7) -> str:
    """
    Generate a response using Groq API.
    - user_input: The user's message.
    - context: Optional previous conversation history.
    - max_tokens: Limit response length.
    - temperature: Controls creativity (0.7 for balanced).
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    if context:
        messages.append({"role": "assistant", "content": context})  # Add history if provided
    
    messages.append({"role": "user", "content": user_input})
    
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",  # Fast, free model; swap to "mixtral-8x7b-32768" for more creativity
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in LLM generation: {e}")
        return "Oops, something went wrong! 😅 Let's try again."
    
import google.generativeai as genai
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')
def generate_response(prompt, ...):
    response = model.generate_content(prompt)
    return response.text