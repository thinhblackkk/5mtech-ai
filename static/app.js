function escapeHTML(text) {

    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

}

let isSending = false;


async function sendMessage() {

    if (isSending) {
        return;
    }

    let input = document.getElementById("question");
    let question = input.value.trim();
    let fileInput = document.getElementById("file-input");
    let file = fileInput.files[0];
    let uploadedFilename = "";
    let safeQuestion = escapeHTML(question);

    if (question === "" && !file) {
        return;
    }

    isSending = true;
    input.disabled = true;

    let chat = document.getElementById("chat");

    chat.innerHTML += `
        <div class="user">
            <span>
                <b>Bạn:</b> ${safeQuestion}
            </span>
        </div>
    `;

    chat.innerHTML += `
        <div class="bot" id="thinking">
            <span>
                ⏳ 5mtech đang suy nghĩ...
            </span>
        </div>
    `;

    chat.scrollTop = chat.scrollHeight;


    try {

        let formData = new FormData();
        formData.append("question", question);
        if (file) {

            let uploadData = new FormData();

            uploadData.append("file", file);

            let uploadResponse = await fetch("/upload", {
                method: "POST",
                body: uploadData
            });

            let uploadResult = await uploadResponse.json();

            if (!uploadResponse.ok) {
                throw new Error(uploadResult.error || "Upload file thất bại.");
            }

            uploadedFilename = uploadResult.filename;
            formData.append("filename", uploadedFilename);

        }

        let response = await fetch("/chat", {

            method: "POST",

            body: formData

        });


        let data = await response.json();

        if (!response.ok) {

    let thinking = document.getElementById("thinking");

    if (thinking) {
        thinking.remove();
    }

    chat.innerHTML += `
        <div class="bot">
            <span>
                <b>5mtech:</b> ${data.error}
            </span>
        </div>
    `;

    input.value = "";
    input.disabled = false;
    isSending = false;

    return;
}

        let thinking = document.getElementById("thinking");

        if (thinking) {
            thinking.remove();
        }


        chat.innerHTML += `
            <div class="bot">
                <span>
                    <b>5mtech:</b> ${escapeHTML(data.answer)}
                </span>
            </div>
        `;


    } catch (error) {

        let thinking = document.getElementById("thinking");

        if (thinking) {
            thinking.remove();
        }

        chat.innerHTML += `
            <div class="bot">
                <span>
                    <b>5mtech:</b> Có lỗi kết nối tới server.
                </span>
            </div>
        `;

        console.error(error);

    }


    input.value = "";

    fileInput.value = "";
    document.getElementById("file-name").textContent = "";

    input.disabled = false;
    isSending = false;

    input.focus();

    chat.scrollTop = chat.scrollHeight;

}



async function loadHistory() {

    let response = await fetch("/history");

    let data = await response.json();

    let chat = document.getElementById("chat");



    data.messages.slice(-20).forEach(message => {
        let name =
            message.role === "user"
            ? "Bạn"
            : "5mtech";


        let type =
            message.role === "user"
            ? "user"
            : "bot";


        chat.innerHTML += `
            <div class="${type}">
                <span>
                    <b>${name}:</b> ${message.text}
                </span>
            </div>
        `;

    });


    chat.scrollTop = chat.scrollHeight;

}



loadHistory();



document.getElementById("question").addEventListener(
    "keydown",
    function(event) {

        if (event.key === "Enter") {

            event.preventDefault();

            sendMessage();

        }

    }
);
document.getElementById("file-input").addEventListener(
    "change",
    function() {

        let file = this.files[0];
        let fileName = document.getElementById("file-name");

        if (file) {
            fileName.textContent = file.name;
        } else {
            fileName.textContent = "";
        }

    }
);
document.getElementById("clear-chat").addEventListener("click", async function() {

    let response = await fetch("/clear", {
        method: "POST"
    });

    let data = await response.json();

    if(data.success){

        let chat = document.getElementById("chat");

        chat.innerHTML = "";

    }

});