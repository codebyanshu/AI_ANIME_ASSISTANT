import os
import time
import requests
import smtplib
import pyautogui
import webbrowser
import feedparser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import ddgs
from typing import Optional


class ActionController:
    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self.log_file = "action_controller_log.txt"
        self.running = True
        self.with_search = ddgs.DDGS()
        self._log("Action Controller initialized.")

    # ---------------- LOGGING ----------------
    def _log(self, message: str):
        timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} {message}\n")

    # ---------------- DRIVER ----------------
    def _init_driver(self):
        if self.driver is not None:
            return self.driver

        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        )

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)
        return self.driver

    # ---------------- COMMAND EXECUTION ----------------
    def execute_command(self, command_dict: dict):
        intent = command_dict.get("intent")
        params = command_dict.get("params", {})

        try:
            if intent == "open_url":
                url = params.get("url", "https://google.com")
                driver = self._init_driver()
                driver.get(url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                return True, f"Opened {url}"

            elif intent == "scroll_down":
                driver = self._init_driver()
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                return True, "Scrolled down."

            elif intent == "scroll_up":
                driver = self._init_driver()
                driver.execute_script("window.scrollTo(0, 0);")
                return True, "Scrolled up."

            elif intent == "send_email":
                return self._send_email(params)

            elif intent == "web_search":
                return self._web_search(params)

            else:
                return False, "Intent not implemented."

        except Exception as e:
            self._log(f"ERROR [{intent}]: {str(e)}")
            return False, str(e)

    # ---------------- HELPERS ----------------
    def _send_email(self, params):
        to_email = params.get("to")
        subject = params.get("subject", "Hello")
        body = params.get("body", "")

        email_user = os.getenv("EMAIL_USER")
        email_pass = os.getenv("EMAIL_PASS")

        if not email_user or not email_pass:
            return False, "EMAIL_USER or EMAIL_PASS not set."

        msg = MIMEMultipart()
        msg["From"] = email_user
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587, timeout=20)
            server.starttls()
            server.login(email_user, email_pass)
            server.sendmail(email_user, to_email, msg.as_string())
            server.quit()
            return True, f"Email sent to {to_email}"
        except Exception as e:
            return False, str(e)

    def _web_search(self, params):
        query = params.get("query", "")
        try:
            results = list(self.with_search.text(query, max_results=3))
            if not results:
                return False, "No results."
            titles = []
            for r in results:
                if isinstance(r, dict):
                    title = r.get("title") or r.get("text") or r.get("snippet")
                    if title:
                        titles.append(title)
                        continue
                titles.append(str(r))
            text = " | ".join(titles)
            return True, text
        except Exception as e:
            return False, str(e)

    # ---------------- CLEANUP ----------------
    def shutdown(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            self._log("Driver closed.")
