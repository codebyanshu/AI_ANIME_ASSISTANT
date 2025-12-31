import subprocess
import platform
import re
import difflib
import os
import time
import pywhatkit as pwk  # For WhatsApp automation
import smtplib  # No installation needed
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyautogui  # For general UI automation like calling
import requests  # For downloads, APIs
import smtplib  # For email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json  # For API responses
from datetime import datetime, timedelta  # For reminders
import webbrowser  # For quick opens
from duckduckgo_search import DDGS  # For web search (pip install duckduckgo-search)
import random  # For jokes

# Safety Features (Updated):
# - Whitelisted commands only.
# - No confirmations (as requested).
# - Logs actions.
# - Rate limiting can be added externally.
# - For email: Use env vars for credentials (never hardcode).

# WARNING: Without confirmations, actions are executed immediately—use responsibly!
# Requires: pip install pywhatkit selenium pyautogui requests duckduckgo-search
# For Selenium: Download ChromeDriver and ensure it's in PATH.
# For email: Set EMAIL_USER and EMAIL_PASS env vars.
# Test in a safe environment.

class ActionController:
    def __init__(self):
        self.driver = None  # Selenium driver for web tasks
        self.log_file = "action_controller_log.txt"
        self._log("Action Controller initialized.")
        self.running = True
        self.with_search = DDGS()  # DuckDuckGo search instance

    def _log(self, message):
        """Log actions to file with timestamp."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
        print(f"LOG: {message}")

    def get_os(self) -> str:
        system = platform.system()
        if system == "Windows":
            return "windows"
        if system == "Darwin":
            return "darwin"
        return "linux"

    def normalize_command(self, text: str) -> dict:
        """
        Parse and normalize voice command into structured intent.
        Returns dict: {'intent': 'send_email', 'params': {'to': 'user@example.com', 'subject': 'hi', 'body': 'hello'}}
        """
        text = text.lower().strip()
        text = re.sub(r"[^\w\s@+:/.,]", " ", text)  # Clean punctuation, keep essentials

        # Fillers to ignore
        fillers = {"please", "the", "to", "a", "an", "hey", "hi", "ok", "yeah", "tell", "me", "about"}
        words = [w for w in text.split() if w not in fillers]
        cleaned = " ".join(words)

        # Expanded intents with aliases
        intents = {
            # Original/Core
            "open settings": {"intent": "open_settings"},
            "open chrome": {"intent": "open_browser"},
            "sleep computer": {"intent": "sleep"},

            # Communication
            "send whatsapp": {"intent": "send_whatsapp"},
            "message on whatsapp": {"intent": "send_whatsapp"},
            "whatsapp to": {"intent": "send_whatsapp"},
            "call": {"intent": "make_call"},
            "phone": {"intent": "make_call"},
            "dial": {"intent": "make_call"},
            "send email": {"intent": "send_email"},
            "email to": {"intent": "send_email"},

            # Web
            "open website": {"intent": "open_url"},
            "go to": {"intent": "open_url"},
            "browse": {"intent": "open_url"},
            "scroll down": {"intent": "scroll_down"},
            "scroll up": {"intent": "scroll_up"},
            "download": {"intent": "download_file"},
            "search": {"intent": "web_search"},
            "google": {"intent": "web_search"},

            # Utilities
            "play music": {"intent": "play_music"},
            "open notepad": {"intent": "open_notepad"},
            "take screenshot": {"intent": "screenshot"},
            "set reminder": {"intent": "set_reminder"},
            "weather in": {"intent": "get_weather"},
            "news": {"intent": "get_news"},
            "joke": {"intent": "tell_joke"},
            "translate": {"intent": "translate"},
            "calculate": {"intent": "calculate"},
        }

        # Find closest match
        match = difflib.get_close_matches(cleaned, intents.keys(), n=1, cutoff=0.6)
        if not match:
            return {"intent": "unknown", "params": {}}

        base_intent = intents[match[0]]
        params = {}

        # Extract params based on intent
        if base_intent["intent"] in ["send_whatsapp", "make_call", "send_email"]:
            # Extract recipient (number or email)
            recip_match = re.search(r'(\+?\d{10,15}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
            if recip_match:
                params["to"] = recip_match.group(1)
            if base_intent["intent"] == "send_whatsapp":
                msg_start = text.find(params.get("to", "")) + len(params.get("to", ""))
                params["message"] = text[msg_start:].strip() or "Hello!"
            elif base_intent["intent"] == "send_email":
                # Extract subject and body
                subj_match = re.search(r'subject\s+([^\s,]+)', text)
                params["subject"] = subj_match.group(1) if subj_match else "Quick Note"
                body_start = text.find("say") if "say" in text else len(text)
                params["body"] = text[body_start:].strip() or "Hello!"

        elif base_intent["intent"] == "open_url":
            url_match = re.search(r'(https?://[^\s]+|www\.[^\s]+)', text)
            if url_match:
                params["url"] = url_match.group(1)
                if not params["url"].startswith("http"):
                    params["url"] = "https://" + params["url"]

        elif base_intent["intent"] in ["download_file", "web_search"]:
            query_match = re.search(r'(https?://[^\s]+|[^\s]+)', text)
            params["query"] = query_match.group(1) if query_match else "general"

        elif base_intent["intent"] == "set_reminder":
            # Extract time/message (simple: "remind me in 5 minutes to eat")
            time_match = re.search(r'in\s+(\d+)\s+(minutes?|hours?)', text)
            params["delay"] = int(time_match.group(1)) if time_match else 1
            params["unit"] = time_match.group(2)[:-1] if time_match else "minute"
            params["message"] = text.split("to")[-1].strip() if "to" in text else "Reminder"

        elif base_intent["intent"] == "get_weather":
            params["location"] = re.sub(r'weather in\s+', '', text).strip() or "current"

        elif base_intent["intent"] == "translate":
            # Assume "translate hello to spanish"
            from_lang = re.search(r'translate\s+([^\s]+)\s+to\s+([^\s]+)', text)
            params["text"] = from_lang.group(1) if from_lang else "hello"
            params["target"] = from_lang.group(2) if from_lang else "english"

        elif base_intent["intent"] == "calculate":
            params["expression"] = re.sub(r'calculate\s+', '', text).strip()

        return {"intent": base_intent["intent"], "params": params}

    def can_execute(self, command_dict: dict) -> bool:
        """Check if intent is whitelisted."""
        return command_dict["intent"] in self.get_safe_intents()

    def get_safe_intents(self) -> set:
        """Whitelisted intents (expanded)."""
        return {
            "open_settings", "open_browser", "sleep",
            "send_whatsapp", "make_call", "send_email",
            "open_url", "scroll_down", "scroll_up", "download_file", "web_search",
            "play_music", "open_notepad", "screenshot", "set_reminder",
            "get_weather", "get_news", "tell_joke", "translate", "calculate",
        }

    def execute_command(self, command_dict: dict):
        """Execute the normalized command. Returns (success: bool, message: str)."""
        intent = command_dict["intent"]
        params = command_dict["params"]

        if not self.can_execute(command_dict):
            return False, "Command not allowed for safety."

        try:
            if intent == "open_settings":
                os_name = self.get_os()
                cmd_map = {
                    "windows": ["cmd", "/c", "start", "ms-settings:"],
                    "linux": ["gnome-control-center"],
                    "darwin": ["open", "-a", "System Settings"],
                }
                cmd = cmd_map.get(os_name)
                if cmd:
                    subprocess.Popen(cmd)
                    return True, "Opened settings."
                return False, "Not supported on this OS."

            elif intent == "open_browser":
                subprocess.Popen(["cmd", "/c", "start", "chrome"], shell=True)  # Adjust for OS
                return True, "Opened browser."

            elif intent == "sleep":
                os_name = self.get_os()
                cmd_map = {
                    "windows": ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"],
                    "linux": ["systemctl", "suspend"],
                    "darwin": ["pmset", "sleepnow"],
                }
                cmd = cmd_map.get(os_name)
                if cmd:
                    subprocess.run(cmd)
                    return True, "Computer sleeping."
                return False, "Not supported."

            elif intent == "send_whatsapp":
                number = params.get("to")
                message = params.get("message", "Hello!")
                if number:
                    try:
                        # Prefer instant send if available in the installed pywhatkit
                        if hasattr(pwk, "sendwhatmsg_instantly"):
                            pwk.sendwhatmsg_instantly(number, message)
                        else:
                            # Fallback: open WhatsApp Web with prefilled message and send via UI
                            # Encode message for URL
                            safe_msg = requests.utils.requote_uri(message)
                            url = f"https://web.whatsapp.com/send?phone={number}&text={safe_msg}"
                            webbrowser.open(url)
                            # Wait a short while for the page to load / user to scan QR if needed
                            time.sleep(8)
                            # Press enter to send the message (requires active WhatsApp Web session)
                            pyautogui.press('enter')
                        return True, f"WhatsApp message sent to {number}."
                    except Exception as exc:
                        return False, f"WhatsApp send failed: {str(exc)}"
                return False, "Missing number."

            elif intent == "make_call":
                number = params.get("to")
                if number:
                    if self.get_os() == "windows":
                        os.system(f"cmd /c start tel:{number}")
                    else:
                        pyautogui.hotkey('super', 's')  # Search (Linux/Mac equiv)
                        time.sleep(1)
                        pyautogui.write('phone')
                        pyautogui.press('enter')
                        time.sleep(2)
                        pyautogui.write(number)
                        pyautogui.press('enter')
                    return True, f"Calling {number}."
                return False, "Missing number."

            elif intent == "send_email":
                to_email = params.get("to")
                subject = params.get("subject", "Quick Note")
                body = params.get("body", "Hello!")
                if to_email:
                    # Use env vars for credentials
                    email_user = os.getenv("EMAIL_USER")
                    email_pass = os.getenv("EMAIL_PASS")
                    if not email_user or not email_pass:
                        return False, "Set EMAIL_USER and EMAIL_PASS env vars."
                    msg = MIMEMultipart()
                    msg['From'] = email_user
                    msg['To'] = to_email
                    msg['Subject'] = subject
                    msg.attach(MIMEText(body, 'plain'))
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(email_user, email_pass)
                    text = msg.as_string()
                    server.sendmail(email_user, to_email, text)
                    server.quit()
                    return True, f"Email sent to {to_email}."
                return False, "Missing recipient."

            elif intent == "open_url":
                url = params.get("url", "https://google.com")
                self._init_driver()
                self.driver.get(url)
                return True, f"Opened {url}."

            elif intent == "scroll_down":
                self._init_driver()
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                return True, "Scrolled down."

            elif intent == "scroll_up":
                self._init_driver()
                self.driver.execute_script("window.scrollTo(0, 0);")
                return True, "Scrolled up."

            elif intent == "download_file":
                url = params.get("query")
                filename = params.get("filename", "download")
                if url and url.startswith("http"):
                    response = requests.get(url)
                    if response.status_code == 200:
                        with open(f"{filename}.txt", "wb") as f:  # Default to .txt; adjust
                            f.write(response.content)
                        return True, f"Downloaded to {filename}.txt."
                    return False, "Download failed."
                return False, "Missing URL."

            elif intent == "web_search":
                query = params.get("query", "general")
                results = list(self.with_search.text(query, max_results=3))
                summary = "\n".join([f"{r['title']}: {r['body']}" for r in results])
                return True, f"Search results for '{query}': {summary[:200]}..."  # Truncate for voice

            elif intent == "play_music":
                webbrowser.open("https://music.youtube.com")
                return True, "Opened music player."

            elif intent == "open_notepad":
                subprocess.Popen(["notepad.exe"])
                return True, "Opened Notepad."

            elif intent == "screenshot":
                screenshot = pyautogui.screenshot()
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
                screenshot.save(filename)
                return True, f"Screenshot saved as {filename}."

            elif intent == "set_reminder":
                delay = params.get("delay", 1)
                unit = params.get("unit", "minute")
                message = params.get("message", "Reminder")
                # Simple: Print or use OS notification
                if unit == "minute":
                    wait_time = delay * 60
                else:
                    wait_time = delay * 3600
                time.sleep(wait_time)
                # Fallback: Print (extend with plyer for notifications: pip install plyer)
                print(f"🔔 REMINDER: {message}")
                return True, f"Reminder set for {delay} {unit}(s): {message}"

            elif intent == "get_weather":
                location = params.get("location", "current")
                # Free OpenWeatherMap API (get key from openweathermap.org)
                api_key = os.getenv("WEATHER_API_KEY", "demo")  # Set env var
                url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
                response = requests.get(url).json()
                if response.get("main"):
                    temp = response["main"]["temp"]
                    desc = response["weather"][0]["description"]
                    return True, f"Weather in {location}: {temp}°C, {desc}."
                return False, "Weather fetch failed (check API key)."

            elif intent == "get_news":
                # RSS from BBC (no key needed)
                rss_url = "http://feeds.bbci.co.uk/news/rss.xml"
                response = requests.get(rss_url)
                # Simple parse (extend with feedparser if installed)
                titles = [line for line in response.text.split("<title>") if "BBC" in line][:3]
                headlines = [t.split("</title>")[0] for t in titles if "</title>" in t]
                return True, f"Top news: {' | '.join(headlines[:3])}"

            elif intent == "tell_joke":
                jokes = [
                    "Why don't scientists trust atoms? Because they make up everything!",
                    "Why did the scarecrow win an award? He was outstanding in his field!",
                    "What do you call fake spaghetti? An impasta!"
                ]
                joke = random.choice(jokes)
                return True, f"Here's a joke: {joke}"

            elif intent == "translate":
                text = params.get("text", "hello")
                target = params.get("target", "english")
                # Free LibreTranslate API
                url = "https://libretranslate.de/translate"
                payload = {"q": text, "source": "auto", "target": target, "format": "text"}
                response = requests.post(url, data=payload).json()
                if "translatedText" in response:
                    return True, f"Translation to {target}: {response['translatedText']}"
                return False, "Translation failed."

            elif intent == "calculate":
                expression = params.get("expression", "2+2")
                try:
                    result = eval(expression)  # Safe for simple math; extend with sympy
                    return True, f"Result: {result}"
                except:
                    return False, "Invalid calculation."

            else:
                return False, "Intent not implemented."

        except Exception as exc:
            self._log(f"Error executing {intent}: {str(exc)}")
            return False, f"Error: {str(exc)}"

    def _init_driver(self):
        """Initialize Selenium Chrome driver."""
        if self.driver is None:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            self.driver = webdriver.Chrome(options=chrome_options)
        return self.driver

    def _close_driver(self):
        """Close Selenium driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def shutdown(self):
        """Cleanup on exit."""
        self._close_driver()
        self._log("Action Controller shutdown.")