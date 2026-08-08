from flask import Flask, render_template, request
from fivemtech_ai import FiveMTechAI
from fivemtech_memory import FiveMTechMemory

app = Flask(__name__)

ai = FiveMTechAI()
memory = FiveMTechMemory()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    question = request.json["question"]

    contents = memory.get_contents()

    contents.append({
    "role": "user",
    "parts": [
        {
            "text": question
        }
    ]
})

    response, error = ai.ask(
        contents,
        memory.profile
    )

    if error:

        return {
            "error": "Gemini API đang gặp vấn đề."
        }, 500
    memory_data = ai.extract_memory(question)

    for key, value in memory_data.items():

        memory.update_profile(key, value)

    memory.add_user_message(question)

    memory.add_model_message(response)

    return {
        "answer": response
}
@app.route("/history")
def history():

    return {
        "messages": memory.conversation
    }

@app.route("/clear", methods=["POST"])
def clear():

    memory.clear()

    return {
        "success": True
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)