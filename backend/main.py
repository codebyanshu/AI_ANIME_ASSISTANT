import asyncio
from llm import ask_llm
from text_processing import prepare_speech
from tts import speak
from pc_control import perform_action

async def main():
    while True:
        user = input("You: ")

        if user.lower() in ["exit", "quit"]:
            break

        data = ask_llm(user)

        print("DISPLAY:\n", data.get("display", ""))

        # Prepare speech using heuristics that consider the user's input
        speech = prepare_speech(data, user)
        await speak(speech, data.get("emotion", "calm"))

        # Decide whether to perform a PC action. Trigger when either:
        # - LLM explicitly returned action.type == 'pc'
        # - User's input contains PC-intent keywords (open, send, whatsapp, code, make, search)
        action = data.get("action", {})
        cmd_from_llm = None
        if isinstance(action, dict) and action.get("type") == "pc":
            cmd_from_llm = action.get("command", "")

        pc_keywords = ["send", "whatsapp", "open", "search", "call", "code", "write", "create", "make", "site"]
        user_lower = user.lower()
        user_looks_like_pc = any(k in user_lower for k in pc_keywords)

        if cmd_from_llm or user_looks_like_pc:
            cmd = cmd_from_llm or user
            print(f"DEBUG: main.py deciding command -> cmd_from_llm='{cmd_from_llm}', user='{user}', final_cmd='{cmd}'")
            # pass model display so perform_action can extract code blocks or helpful text
            result = perform_action(cmd, user, data.get("display", ""))
            print("PC ACTION:", result)

        

asyncio.run(main())
