let isSending = false;


async function sendMessage() {

    if (isSending) {
        return;
    }

    let input = document.getElementById("question");
    let question = input.value.trim();

    if (question === "") {
        return;
    }

    isSending = true;
    input.disabled = true;

    let chat = document.getElementById("chat");

    chat.innerHTML += `
        <div class="user">
            <span>
                <b>Bạn:</b> ${question}
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

        let response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question: question
            })

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
                    <b>5mtech:</b> ${data.answer}
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

    input.disabled = false;
    isSending = false;

    input.focus();

    chat.scrollTop = chat.scrollHeight;

}



async function loadHistory() {

    let response = await fetch("/history");

    let data = await response.json();

    let chat = document.getElementById("chat");


    data.messages.forEach(message => {

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