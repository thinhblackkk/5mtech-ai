
from google import genai
import os
from dotenv import load_dotenv

from fivemtech_config import SYSTEM_PROMPT

from fivemtech_memory_parser import FiveMTechMemoryParser

load_dotenv()


class FiveMTechAI:

    def __init__(self):

        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )

        self.memory_parser = FiveMTechMemoryParser()

    def ask(self, contents, profile):

        profile_text = f"""
        THÔNG TIN NGƯỜI DÙNG ĐÃ LƯU:

        {profile}

        Hãy sử dụng những thông tin trên khi phù hợp với câu hỏi.
        Không tự bịa thêm thông tin chưa được lưu.
        """

        contents = [
            {
                "role": "user",
                "parts": [
                    {
                        "text": SYSTEM_PROMPT + profile_text
                    }
                ]
            }
        ] + contents


        try:

            response = self.client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=contents
            )

            return response.text, None


        except Exception as e:

            print("Gemini error:", e)

            error_text = str(e)

            if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:

                return None, {
                    "type": "quota",
                    "error": e
                }

            if "timeout" in error_text.lower():

                return None, {
                    "type": "timeout",
                    "error": e
                }

            if (
                "401" in error_text
                or "403" in error_text
                or "API_KEY" in error_text.upper()
            ):

                return None, {
                    "type": "authentication",
                    "error": e
                }

            return None, {
                "type": "api_error",
                "error": e
            }
    
    
    def extract_memory(self, question):

        return self.memory_parser.extract(question)
