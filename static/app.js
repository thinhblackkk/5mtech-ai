async function sendMessage(){


let input = document.getElementById("question");

let question = input.value;


if(question.trim() === ""){
    return;
}



let chat = document.getElementById("chat");



chat.innerHTML +=
`
<div class="user">
<span>
<b>Bạn:</b> ${question}
</span>
</div>
`;



let response = await fetch("/chat",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({
question:question
})

});



let data = await response.json();



chat.innerHTML +=
`
<div class="bot">
<span>
<b>5mtech:</b> ${data.answer}
</span>
</div>
`;



input.value="";

chat.scrollTop = chat.scrollHeight;


}




async function loadHistory(){


let response = await fetch("/history");


let data = await response.json();


let chat = document.getElementById("chat");



data.messages.forEach(message=>{


let name =
message.role === "user"
? "Bạn"
: "5mtech";


let type =
message.role === "user"
? "user"
: "bot";



chat.innerHTML +=
`
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

