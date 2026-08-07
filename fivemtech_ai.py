from google import genai
import os

from fivemtech_config import SYSTEM_PROMPT


class FiveMTechAI:

    def __init__(self):
        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )

    def ask(self, contents):

        contents.insert(0, {
            "role": "user",
            "parts": [
                {
                    "text": SYSTEM_PROMPT
                }
            ]
        })

        response = self.client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=contents
        )

        return response.text