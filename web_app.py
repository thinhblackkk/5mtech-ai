import os
import pymupdf
from file_reader import read_file
from flask import Flask, render_template, request
from fivemtech_ai import FiveMTechAI
from fivemtech_memory import FiveMTechMemory

DATA_DIR = os.getenv("DATA_DIR", ".")

UPLOAD_DIR = os.path.join(
    DATA_DIR,
    "uploads"
)

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)

app = Flask(__name__)

ai = FiveMTechAI()
memory = FiveMTechMemory()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    question = request.form.get("question", "").strip()

    filename = request.form.get("filename", "").strip()

    print("CHAT FORM:", request.form)

    print("CHAT FILENAME:", filename)

    file_content = ""

    if filename:
        memory.set_file_context(filename)

    elif memory.file_context:
        filename = memory.file_context

    if filename:

        file_path = os.path.join(
            UPLOAD_DIR,
            filename
        )

        if os.path.exists(file_path):

            file_content = read_file(file_path)

    contents = memory.get_contents()

    ai_question = question

    if filename:
        ai_question += f"\n\nNội dung file {filename}:\n{file_content}"

    contents.append({
        "role": "user",
        "parts": [
            {
                "text": ai_question
            }
        ]
    })
    response, error = ai.ask(
        contents,
        memory.profile
    )

    if error:

        print("GEMINI ERROR:", error)

        return {
            "error": "Gemini API đang gặp vấn đề."
        }, 500
    memory_data = ai.extract_memory(question)

    for key, value in memory_data.items():

        memory.update_profile(key, value)

    memory.add_user_message(
        question,
        has_file=bool(filename)
    )

    memory.add_model_message(
    response,
    has_file=bool(filename)
)

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

@app.route("/clear-file", methods=["POST"])
def clear_file():

    memory.clear_file_context()

    return {
        "success": True
    }

@app.route("/upload", methods=["POST"])
def upload():

    if "file" not in request.files:
        return {
            "error": "Chưa chọn file."
        }, 400

    file = request.files["file"]

    if file.filename == "":
        return {
            "error": "Tên file không hợp lệ."
        }, 400

    filename = file.filename

    file_path = os.path.join(
        UPLOAD_DIR,
        filename
    )

    file.save(file_path)

    return {
        "success": True,
        "filename": filename
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)