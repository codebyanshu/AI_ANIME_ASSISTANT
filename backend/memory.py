from collections import deque

class Memory:
    def __init__(self, max_len=6):
        self.history = deque(maxlen=max_len)

    def add(self, user, ai):
        self.history.append(f"User: {user}")
        self.history.append(f"Emily: {ai}")

    def context(self):
        return "\n".join(self.history)
