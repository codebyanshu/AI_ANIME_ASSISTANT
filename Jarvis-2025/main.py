import os
import eel
from backend.auth import recoganize
from backend.auth.recoganize import AuthenticateFace
from backend.feature import *
from backend.command import *



def start():
    # Guard: monkeypatch eel._process_message to tolerate messages without 'value'
    if not hasattr(eel, "_original_process_message"):
        eel._original_process_message = eel._process_message
        def _safe_process_message(message, ws):
            try:
                if isinstance(message, dict) and 'value' in message:
                    return eel._original_process_message(message, ws)
                # If 'value' is missing, try to avoid KeyError by setting a None return
                if isinstance(message, dict):
                    call_id = message.get('id') or message.get('call') or message.get('call_id')
                    if call_id is not None:
                        eel._call_return_values[call_id] = None
            except Exception:
                pass
        eel._process_message = _safe_process_message

    eel.init("frontend") 
    
    play_assistant_sound()
    @eel.expose
    def init():
        eel.hideLoader()
        speak("Welcome to Emily")
        speak("Ready for Face Authentication")
        flag = recoganize.AuthenticateFace()
        if flag ==1:
            speak("Face recognized successfully")
            eel.hideFaceAuth()
            eel.hideFaceAuthSuccess()
            speak("Welcome to Your Assistant")
            eel.hideStart()
            play_assistant_sound()
        else:
            speak("Face not recognized. Please try again")
        
    os.system('start msedge.exe --app="http://127.0.0.1:8000/index.html"')
    
    
    
    eel.start("index.html", mode=None, host="localhost", block=True) 

