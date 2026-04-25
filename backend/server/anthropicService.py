import os
import requests
from dotenv import load_dotenv

load_dotenv()


class AnthropicService:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001").strip()

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is missing in .env file")

    def ask(self, prompt: str, max_tokens: int = 500) -> str:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            },
            timeout=30,
        )

        if response.status_code != 200:
            return f"Claude API error: {response.status_code} - {response.text}"

        data = response.json()
        return data["content"][0]["text"]