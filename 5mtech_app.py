from dotenv import load_dotenv
from fivemtech_ai import FiveMTechAI
from fivemtech_memory import FiveMTechMemory

load_dotenv()

ai = FiveMTechAI()
memory = FiveMTechMemory()

while True:
    question = input("Bạn: ")

    if question.lower() == "exit":
        print("5mtech: Tạm biệt!")
        break

    memory.add_user_message(question)

    contents = memory.get_contents()

    answer = ai.ask(contents)

    print("5mtech:", answer)

    memory.add_model_message(answer)