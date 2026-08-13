import json
import os


class FiveMTechMemory:

    def __init__(self):

        data_dir = os.getenv("DATA_DIR", ".")

        self.file = os.path.join(data_dir, "memory.json")
        self.profile_file = os.path.join(data_dir, "profile.json")

        self.conversation = self.load()
        self.profile = self.load_profile()
        self.file_context = None
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
    def load_profile(self):

        if os.path.exists(self.profile_file):

            with open(self.profile_file, "r", encoding="utf-8") as f:
                return json.load(f)

        return {}
    def save_profile(self):

        with open(self.profile_file, "w", encoding="utf-8") as f:

            json.dump(
                self.profile,
                f,
                ensure_ascii=False,
                indent=4
            )
    def update_profile(self, key, value):

            list_fields = [
                "preferences",
                "skills",
                "goals"
            ]

            if key in list_fields:

                if key not in self.profile:

                    self.profile[key] = []

                for item in value:

                    if item not in self.profile[key]:

                        self.profile[key].append(item)

            else:

                self.profile[key] = value

            self.save_profile()
    def add_user_message(self, text):

        self.conversation.append({
            "role": "user",
            "text": text
        })

        self.save()
    def clear(self):

        self.conversation = []
        self.file_context = None
        self.save()

    def add_model_message(self, text):

        self.conversation.append({
            "role": "model",
            "text": text
        })

        self.save()

    def get_contents(self):

        contents = []
        recent_messages = self.conversation[-20:]
        for message in recent_messages:

            contents.append({
                "role": message["role"],
                "parts": [
                    {
                        "text": message["text"]
                    }
                ]
            })

        return contents

    def set_file_context(self, filename):

        self.file_context = filename


    def clear_file_context(self):

        self.file_context = None