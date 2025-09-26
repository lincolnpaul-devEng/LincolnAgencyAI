import os
from openai import OpenAI

class AIClient:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")

        if self.openai_key:
            self.provider = "openai"
            self.client = OpenAI(api_key=self.openai_key)
        elif self.gemini_key:
            try:
                import google.generativeai as genai
            except ImportError as e:
                raise ImportError("google-generativeai is required for Gemini. Install it with: pip install google-generativeai") from e
            self.provider = "gemini"
            genai.configure(api_key=self.gemini_key)
            self.client = genai
        else:
            raise ValueError("No API key found. Set OPENAI_API_KEY or GEMINI_API_KEY.")

    def generate(self, prompt):
        if self.provider == "openai":
            return self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            ).choices[0].message.content
        else:  # Gemini
            response = self.client.GenerativeModel("gemini-pro").generate_content(prompt)
            return response.text
