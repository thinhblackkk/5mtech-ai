from google import genai
import os
from dotenv import load_dotenv

from fivemtech_config import SYSTEM_PROMPT

load_dotenv()


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


        try:

            response = self.client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=contents
            )

            return response.text


        except Exception as e:

            print("Gemini error:", e)

            return "Xin lỗi, hiện tại tao đang hết lượt suy nghĩ. Chờ một chút rồi thử lại nhé."