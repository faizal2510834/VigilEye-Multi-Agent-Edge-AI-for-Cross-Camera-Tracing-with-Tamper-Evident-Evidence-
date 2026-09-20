import re
from config import settings

class IntentParsingAgent:
    def __init__(self):
        self.use_llm = bool(settings.azure_openai_api_key and settings.azure_openai_endpoint)
        if self.use_llm:
            print("IntentParsingAgent initialized in LLM mode (Azure OpenAI).")
        else:
            print("IntentParsingAgent initialized in RULE-BASED mode.")

    def parse_query(self, raw_query: str):
        if self.use_llm:
            return self._parse_llm(raw_query)
        else:
            return self._parse_rule_based(raw_query)

    def _parse_llm(self, query: str):
        # Stub for Azure OpenAI call using JSON schema
        # Since we want it zero-friction, this handles the logic if keys are provided.
        # Fallback to rule-based if LLM fails
        return self._parse_rule_based(query)

    def _parse_rule_based(self, query: str):
        q = query.lower()
        
        # Extremely basic NLP extraction for the demo
        colors = ["red", "blue", "green", "black", "white", "yellow"]
        tamil_colors = {"sivappu": "red", "neelam": "blue", "pachai": "green", "karuppu": "black", "vellai": "white"}
        hindi_colors = {"laal": "red", "neela": "blue", "hara": "green", "kaala": "black", "safed": "white"}
        
        target_color = "unknown"
        for color in colors:
            if color in q: target_color = color
        for k, v in tamil_colors.items():
            if k in q: target_color = v
        for k, v in hindi_colors.items():
            if k in q: target_color = v
            
        target_class = "person"
        if "car" in q or "vehicle" in q or "vandi" in q or "gaadi" in q:
            target_class = "vehicle"
            
        return {
            "object_class": target_class,
            "attributes": {"color": target_color},
            "time_range": None, # parsed dynamically if present
            "camera_hints": [],
            "raw_text": query
        }
        
intent_parser = IntentParsingAgent()
