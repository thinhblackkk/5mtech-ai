from google import genai
import os


class FiveMTechAI:

    def __init__(self):
        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )

    def ask(self, contents):
        response = self.client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=contents
        )

        return response.text