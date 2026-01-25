import os
import webbrowser
import urllib.parse
import subprocess
import shutil
import platform
from typing import Optional


def send_whatsapp(message: str, phone: Optional[str] = None, contact_name: Optional[str] = None) -> str:
	"""Try to open WhatsApp and (optionally) automate sending to a contact name.

	Behavior:
	- If `phone` is provided, prefer `wa.me` or protocol with phone.
	- If `contact_name` is provided (no phone), attempt to open WhatsApp and
	  use optional automation (`pyperclip` + `pyautogui`) to search the contact
	  then paste & send the message.
	- If automation packages aren't installed, fall back to opening WhatsApp Web
	  and inform the user.
	"""
	quoted = urllib.parse.quote(message or "")

	# Helper to attempt automation: type contact name (if any), paste message, send
	def try_automation(msg: str, contact: Optional[str]) -> bool:
		try:
			import time
			import pyperclip
			import pyautogui
			time.sleep(1.5)
			if contact:
				# Try to reliably focus WhatsApp's contact search, then clear and type
				# (Ctrl+K focuses search in WhatsApp Web/desktop; fallback to Ctrl+F)
				pyautogui.hotkey('ctrl', 'k')
				time.sleep(0.2)
				# ensure search is empty
				pyautogui.hotkey('ctrl', 'a')
				pyautogui.press('backspace')
				pyautogui.typewrite(contact, interval=0.03)
				time.sleep(0.3)
				pyautogui.press('enter')
				# allow chat to open and input to focus
				time.sleep(1.0)
			pyperclip.copy(msg)
			pyautogui.hotkey('ctrl', 'v')
			time.sleep(0.05)
			pyautogui.press('enter')
			return True
		except Exception:
			return False

	# 1) Try protocol handler first — only when we have a phone number or no
	# contact_name. If a contact_name is provided we avoid protocol because some
	# handlers prefill the message and that can interfere with the search input.
	use_protocol = bool(phone or not contact_name)
	if use_protocol:
		try:
			if phone:
				prot = f"whatsapp://send?phone={phone}&text={quoted}"
			else:
				prot = f"whatsapp://send?text={quoted}"

			if platform.system() == "Windows":
				os.startfile(prot)
			else:
				webbrowser.open(prot)

			if try_automation(message, contact_name):
				_target = contact_name or phone
				_suffix = f" to {_target}" if _target else ""
				return f"Opened native WhatsApp and attempted to search contact & send message{_suffix}."
			_target = contact_name or phone
			_suffix = f" to {_target}" if _target else ""
			return f"Opened native WhatsApp (protocol) with message{_suffix}. Automation unavailable."
		except Exception:
			# Protocol failed — continue to next fallback
			pass

	# 2) Try known exe locations (desktop app)
	exe_candidates = []
	local = os.environ.get("LOCALAPPDATA")
	if local:
		exe_candidates.append(os.path.join(local, "Programs", "WhatsApp", "WhatsApp.exe"))
		exe_candidates.append(os.path.join(local, "WhatsApp", "WhatsApp.exe"))
	exe_candidates.append(r"C:\Program Files\WhatsApp\WhatsApp.exe")
	exe_candidates.append(r"C:\Program Files (x86)\WhatsApp\WhatsApp.exe")

	for exe in exe_candidates:
		try:
			if exe and os.path.exists(exe):
				subprocess.Popen([exe])
				if try_automation(message, contact_name):
					return f"Opened WhatsApp desktop app ({exe}) and attempted to search contact & send message."
				return f"Opened WhatsApp desktop app ({exe}). Message may need manual paste. Automation unavailable."
		except Exception:
			continue

	# 3) Final fallback: open WhatsApp Web. If contact_name provided, open main web and
	# rely on automation to search; otherwise open send URL with prefilled text.
	if phone:
		url = f"https://wa.me/{phone}?text={quoted}"
	else:
		if contact_name:
			url = "https://web.whatsapp.com"
		else:
			url = f"https://web.whatsapp.com/send?text={quoted}"

	webbrowser.open(url)
	_target = contact_name or phone
	_suffix = f" to {_target}" if _target else ""
	return f"Opened WhatsApp Web with message{_suffix}."


def make_call(number: str) -> str:
	url = f"tel:{number}"
	try:
		webbrowser.open(url)
		return f"Attempted to start a call to {number}."
	except Exception as e:
		return f"Failed to start call: {e}"


def google_search(query: str) -> str:
	url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
	webbrowser.open(url)
	return f"Opened Google search for: {query}"


def open_url(url: str) -> str:
	webbrowser.open(url)
	return f"Opened URL: {url}"


def write_code_in_vscode(path: str, content: str) -> str:
	# Ensure directory exists
	os.makedirs(os.path.dirname(path), exist_ok=True)
	with open(path, "w", encoding="utf-8") as f:
		f.write(content)

	# Try to open in VS Code using `code` CLI, fallback to OS default
	try:
		subprocess.Popen(["code", path], shell=True)
		return f"Wrote file and opened in VS Code: {path}"
	except Exception:
		try:
			os.startfile(path)
			return f"Wrote file and opened with default app: {path}"
		except Exception as e:
			return f"Wrote file but failed to open editor: {e}"


def compose_mail(subject: str, body: str, to: Optional[str] = None) -> str:
	mailto = "mailto:"
	if to:
		mailto += urllib.parse.quote(to)
	params = {}
	if subject:
		params["subject"] = subject
	if body:
		params["body"] = body
	if params:
		mailto += "?" + urllib.parse.urlencode(params)
	webbrowser.open(mailto)
	return f"Opened mail composer{' to ' + to if to else ''}."


def perform_action(command: str, raw_text: str = "", model_output: str = "") -> str:
	"""Simple keyword router for PC actions based on a textual command.

	This is intentionally conservative: it opens browser links or writes files.
	"""
	lc = command.lower()

	# App launches: common desktop apps
	if "open" in lc and ("chrome" in lc or "google chrome" in lc):
		return open_application("chrome")

	if "open" in lc and ("calculator" in lc or "calc" in lc):
		return open_application("calculator")

	if "open" in lc and ("notepad" in lc or "editor" in lc):
		return open_application("notepad")

	# generic browser/open
	if "open" in lc and ("browser" in lc or "internet" in lc):
		webbrowser.open("https://www.google.com")
		return "Opened default browser to Google."

	# WhatsApp — try to extract both message and recipient (name or phone)
	if "whatsapp" in lc or "whatsap" in lc:
		import re
		msg = None
		recipient = None

		# 1) Pattern: send "message" to Recipient on whatsapp
		m = re.search(r"send\s+['\"](?P<msg>.+?)['\"]\s+to\s+(?P<recipient>[\w\s\.\-+@]+)(?:\s+on\s+whatsapp)?", command, re.I)
		if m:
			msg = m.group('msg').strip()
			recipient = m.group('recipient').strip()

		# 2) Pattern: send message_text to Recipient on whatsapp (no quotes)
		if not msg:
			m2 = re.search(r"send\s+(?P<msg>[^\n]+?)\s+to\s+(?P<recipient>[\w\s\.\-+@]+)(?:\s+on\s+whatsapp)?", command, re.I)
			if m2:
				# avoid matching commands like 'send helo to manpreet' where msg may include extra words
				msg = m2.group('msg').strip()
				recipient = m2.group('recipient').strip()

		# 3) fallback: quoted message anywhere
		if not msg:
			q = re.search(r"['\"](.+?)['\"]", command)
			if q:
				msg = q.group(1).strip()

		# 4) fallback: 'message: text' style
		if not msg:
			m3 = re.search(r"message(?: to)?(?: [\w+\-@]*)?:?\s*['\"]?(.+?)['\"]?$", command, re.I)
			if m3:
				msg = m3.group(1).strip()

		# ultimately fallback to raw_text or empty
		if not msg:
			msg = raw_text or ""

		# Determine if recipient is a phone number
		phone = None
		contact_name = None
		if recipient:
			digits = re.sub(r"\D", "", recipient)
			if len(digits) >= 7:
				phone = digits
			else:
				contact_name = recipient

		return send_whatsapp(msg, phone=phone, contact_name=contact_name)

	if "call" in lc and any(ch.isdigit() for ch in lc):
		# extract digits
		import re
		digits = re.sub(r"\D", "", lc)
		return make_call(digits)

	if "search" in lc or "google" in lc:
		# try to extract after 'search' or 'for'
		q = raw_text or command
		return google_search(q)

	if "open url" in lc or "open" in lc and "http" in lc:
		# extract url
		import re
		m = re.search(r"(https?://[\w\-./?=&%]+)", command)
		if m:
			return open_url(m.group(1))

	if "code" in lc or "write code" in lc or "create file" in lc or "make" in lc or "site" in lc:
		# Try to extract code block from the user's command first; if not found,
		# try the model output which often contains the code block.
		import re
		m = re.search(r"```(?:python|js|txt)?\n([\s\S]+?)```", command)
		if not m and model_output:
			m = re.search(r"```(?:python|js|txt)?\n([\s\S]+?)```", model_output)

		if m:
			content = m.group(1)
			# attempt to extract filename from command or model output
			fm = re.search(r"file(?: named| called)?\s+([\w\.\-/]+)", command)
			if not fm and model_output:
				fm = re.search(r"file(?: named| called)?\s+([\w\.\-/]+)", model_output)
			filename = fm.group(1) if fm else os.path.join(os.getcwd(), "assistant_out.py")
			return write_code_in_vscode(filename, content)
		else:
			# If no code block but user asked to make a site or write code, ask the model
			# (we already have model_output) — attempt to extract inline code-like text
			inline = None
			if model_output:
				# look for lines that resemble code (contains def/class/<>/function)
				lines = [l for l in model_output.splitlines() if any(kw in l for kw in ("def ", "class ", "<html", "function "))]
				if lines:
					inline = "\n".join(model_output.splitlines())
			if inline:
				filename = os.path.join(os.getcwd(), "assistant_out.py")
				return write_code_in_vscode(filename, inline)
			return "No code block found to write."

	if "mail" in lc or "email" in lc or "compose" in lc:
		# try to extract subject/body
		import re
		subj = ""
		body = raw_text or ""
		sm = re.search(r"subject\s*[:\-]\s*['\"]?([^'\"]+)['\"]?", command, re.I)
		if sm:
			subj = sm.group(1)
		bm = re.search(r"body\s*[:\-]\s*['\"]([\s\S]+?)['\"]", command, re.I)
		if bm:
			body = bm.group(1)
		return compose_mail(subj, body)

	return "No matching PC action found."


def open_application(name: str) -> str:
	name = name.lower()
	candidates = []
	if "chrome" in name:
		candidates = [
			"chrome",
			"google-chrome",
			r"C:\Program Files\Google\Chrome\Application\chrome.exe",
			r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
		]
	elif "edge" in name:
		candidates = [
			"msedge",
			r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
			r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
		]
	elif "firefox" in name:
		candidates = ["firefox"]
	elif "calculator" in name or "calc" in name:
		candidates = ["calc.exe"]
	elif "notepad" in name:
		candidates = ["notepad.exe"]
	else:
		return f"No known app mapping for '{name}'."

	last_err = None
	for c in candidates:
		try:
			exe = None
			if os.path.exists(c):
				exe = c
			else:
				exe = shutil.which(c)

			if not exe:
				continue

			# On Windows prefer direct execution; avoid shell=True where possible
			if platform.system() == "Windows":
				subprocess.Popen([exe], shell=False)
			else:
				subprocess.Popen([exe])
			return f"Opened {name} ({exe})."
		except Exception as e:
			last_err = e

	return f"Failed to open {name}. {last_err or ''}"