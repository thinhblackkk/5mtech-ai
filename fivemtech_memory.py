class FiveMTechMemory:

    def __init__(self):
        self.conversation = []

    def add_user_message(self, text):
        self.conversation.append({
            "role": "user",
            "text": text
        })

    def add_model_message(self, text):
        self.conversation.append({
            "role": "model",
            "text": text
        })

    def get_contents(self):
        contents = []

        for message in self.conversation:
            contents.append({
                "role": message["role"],
                "parts": [
                    {"text": message["text"]}
                ]
            })

        return contents