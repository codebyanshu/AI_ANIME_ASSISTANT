def prepare_speech(data: dict) -> str:
    address = data.get("address", "none")
    speak = data.get("speak", "")

    if address == "sir":
        speak = f"Sir, {speak}"
    elif address == "master":
        speak = f"Master, {speak}"

    return speak.strip()
