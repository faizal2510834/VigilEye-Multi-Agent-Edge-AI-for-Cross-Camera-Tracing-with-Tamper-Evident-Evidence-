import asyncio
from typing import Callable, Dict, List

class MessageBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.message_history = []

    def subscribe(self, topic: str, callback: Callable):
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)

    async def publish(self, topic: str, message: dict):
        # Save to history for SSE streaming to the frontend
        self.message_history.append({"topic": topic, "message": message})
        if len(self.message_history) > 100:
            self.message_history.pop(0)

        if topic in self.subscribers:
            for callback in self.subscribers[topic]:
                # Fire and forget
                asyncio.create_task(callback(message))

bus = MessageBus()
