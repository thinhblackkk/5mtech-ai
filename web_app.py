import os
import pymupdf
from file_reader import read_file
from data_analyzer import analyze_file
from data_query import query_file
from flask import Flask, render_template, request
from fivemtech_ai import FiveMTechAI
from fivemtech_memory import FiveMTechMemory
from werkzeug.utils import secure_filename

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
    analysis_result = None
    query_result = None

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

        extension = os.path.splitext(
            filename
        )[1].lower()

        if extension in [".csv", ".xlsx"]:

            try:

                analysis_result = analyze_file(
                    file_path
                )

            except Exception as e:

                print(
                    "DATA ANALYSIS ERROR:",
                    e
                )
        try:

            query_result = query_file(
                file_path,
                question
            )

        except Exception as e:

            print(
                "DATA QUERY ERROR:",
                e
            )
    if query_result is not None:

        result_type = query_result.get("type")
        answer = None

        if result_type == "person":

            row = query_result["row"]
            column = query_result.get("column")
            value = query_result.get("value")

            if column and value is not None:

                answer = (
                    f"Dựa trên dữ liệu từ sheet "
                    f"**{query_result['sheet']}**, "
                    f"**{column}** của **{row.get('Tên')}** "
                    f"là **{value:,}**."
                )

            else:

                details = ", ".join(
                    f"**{key}**: {value}"
                    for key, value in row.items()
                )

                answer = (
                    f"Dựa trên dữ liệu từ sheet "
                    f"**{query_result['sheet']}**: "
                    f"{details}"
                )

        elif result_type == "sum":

            answer = (
                f"Dựa trên dữ liệu từ sheet "
                f"**{query_result['sheet']}**, "
                f"tổng **{query_result['column']}** là "
                f"**{query_result['value']:,}**."
            )

        elif result_type == "sum_filtered":

            operator_text = {
                ">": "trên",
                ">=": "từ",
                "<": "dưới",
                "<=": "không quá"
            }.get(
                query_result.get("operator"),
                ""
            )

            value = query_result.get("value")

            answer = (
                f"Dựa trên dữ liệu từ sheet "
                f"**{query_result['sheet']}**, "
                f"tổng **{query_result['column']}** "
                f"của những người {operator_text} "
                f"**{value:,.0f}** là "
                f"**{query_result['sum']:,}**."
            )

        elif result_type == "average":

            answer = (
                f"Dựa trên dữ liệu từ sheet "
                f"**{query_result['sheet']}**, "
                f"giá trị trung bình của "
                f"**{query_result['column']}** là "
                f"**{query_result['value']:,.0f}**."
            )

        elif result_type in ["max", "min"]:

            rows = query_result["rows"]

            names = ", ".join(
                f"**{row.get('Tên', 'Không rõ')}**"
                for row in rows
            )

            label = (
                "cao nhất"
                if result_type == "max"
                else "thấp nhất"
            )

            answer = (
                f"Dựa trên dữ liệu từ sheet "
                f"**{query_result['sheet']}**, "
                f"{names} có "
                f"{query_result['column']} {label}: "
                f"**{query_result['value']:,}**."
            )

        elif result_type == "filtered_aggregate":

            rows = query_result["rows"]

            if not rows:

                answer = "Không tìm thấy dữ liệu phù hợp."

            else:

                operator_text = {
                    ">": "trên",
                    ">=": "từ",
                    "<": "dưới",
                    "<=": "không quá"
                }.get(
                    query_result.get("operator"),
                    ""
                )

                value = query_result.get("value")

                names = ", ".join(
                    f"**{row.get('Tên', 'Không rõ')}**"
                    for row in rows
                )

                answer = (
                    f"Dựa trên dữ liệu từ sheet "
                    f"**{query_result['sheet']}**, "
                    f"có **{len(rows)}** người có "
                    f"**{query_result['column']} {operator_text} "
                    f"{value:,.0f}**: {names}."
                )

        elif result_type == "filtered_range":

            rows = query_result["rows"]

            if not rows:

                answer = "Không tìm thấy dữ liệu phù hợp."

            else:

                names = ", ".join(
                    f"**{row.get('Tên', 'Không rõ')}**"
                    for row in rows
                )

                answer = (
                    f"Dựa trên dữ liệu từ sheet "
                    f"**{query_result['sheet']}**, "
                    f"có **{len(rows)}** kết quả trong khoảng "
                    f"**{query_result['min_value']:,.0f} - "
                    f"{query_result['max_value']:,.0f}**: "
                    f"{names}."
                )

        elif result_type == "filtered":

            rows = query_result["rows"]

            if not rows:

                answer = "Không tìm thấy dữ liệu phù hợp."

            else:

                names = ", ".join(
                    f"**{row.get('Tên', 'Không rõ')}**"
                    for row in rows
                )

                answer = (
                    f"Dựa trên dữ liệu từ sheet "
                    f"**{query_result['sheet']}**, "
                    f"có **{len(rows)}** kết quả: "
                    f"{names}."
                )

        if answer is not None:

            memory.add_user_message(
                question,
                has_file=bool(filename)
            )

            memory.add_model_message(
                answer
            )

            return {
                "answer": answer
            }
    contents = memory.get_contents()

    ai_question = question

    if filename:

        ai_question += (
            f"\n\nNội dung file {filename}:\n"
            f"{file_content}"
        )

        if analysis_result is not None:

            ai_question += (
                "\n\nKẾT QUẢ PHÂN TÍCH "
                "BẰNG PYTHON:\n"
                f"{analysis_result}"
            )
        if query_result is not None:

            ai_question += (
                "\n\nKẾT QUẢ TRUY VẤN BẰNG PYTHON:\n"
                f"{query_result}\n\n"
                "QUY TẮC QUAN TRỌNG: "
                "Kết quả truy vấn bằng Python là nguồn dữ liệu chính xác "
                "cho câu hỏi này. Hãy ưu tiên và sử dụng chính xác kết quả "
                "này để trả lời người dùng. Không tự suy diễn hoặc thay đổi "
                "các giá trị trong kết quả truy vấn."
            )
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

    filename = secure_filename(file.filename)

    if not filename:
        return {
            "error": "Tên file không hợp lệ."
        }, 400

    allowed_extensions = {
        ".xlsx",
        ".csv",
        ".pdf",
        ".txt"
    }

    extension = os.path.splitext(
        filename
    )[1].lower()

    if extension not in allowed_extensions:

        return {
            "error": (
                "Định dạng file chưa được hỗ trợ. "
                "Chỉ hỗ trợ XLSX, CSV, PDF và TXT."
            )
        }, 400

    file_path = os.path.join(
        UPLOAD_DIR,
        filename
    )

    file.save(file_path)

    memory.set_file_context(filename)

    return {
        "success": True,
        "filename": filename
    }
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
