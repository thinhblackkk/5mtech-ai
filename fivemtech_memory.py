import json
import os


class FiveMTechMemory:

    def __init__(self):
        self.file = "memory.json"
        self.conversation = self.load()

    def load(self):

        if os.path.exists(self.file):
            with open(self.file, "r", encoding="utf-8") as f:
                return json.load(f)

        return []

    def save(self):

        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(
                self.conversation,
                f,
                ensure_ascii=False,
                indent=4
            )

    def add_user_message(self, text):

        self.conversation.append({
            "role": "user",
            "text": text
        })

        self.save()

    def add_model_message(self, text):

        self.conversation.append({
            "role": "model",
            "text": text
        })

        self.save()

    def get_contents(self):

        contents = []

        for message in self.conversation:

            contents.append({
                "role": message["role"],
                "parts": [
                    {
                        "text": message["text"]
                    }
                ]
            })

        return contents