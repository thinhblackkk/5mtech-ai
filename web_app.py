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

    memory.add_user_message(question)

    response = ai.ask(
        memory.get_contents()
    )

    memory.add_model_message(response)

    return {"answer": response}


if __name__ == "__main__":
    app.run(debug=True)