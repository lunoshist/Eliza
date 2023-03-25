const apiKey = "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"; // Remplacez VOTRE_CLÉ_D'API_CHATGPT par votre clé d'API ChatGPT

const inputField = document.getElementById("user-message");

var systemMessage = {"role": "system", "content": "People come on this website to speak with Albert Einstein. You are Albert Einstein. Make the user feel like this is a real discussion, like you were old friend, so answer as Einstein would if we were talking to him. And try to be consise. You are not here to discuss subjects related to science and philosophy, but also and especially about private life. If the discussion is coming to an end, take an interest in the user, ask questions about him/her"};
var prevMessages = [] 

// Fonction pour envoyer une demande à l'API de ChatGPT
async function sendRequestToChatGPT(message) {

    const apiRequestBody = {
        "model": "gpt-3.5-turbo",
        "messages": [
            systemMessage,
            ...prevMessages,
        ]
    }

    const response = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${apiKey}`,
        },
        body: JSON.stringify(apiRequestBody)
    });

    const data = await response.json();
    let content = data.choices[0].message.content
    console.log(content.trim());
    prevMessages.push({"role": "assistant", "content": `${content}`},)

    if (data.usage.total_tokens > 3500) {
        prevMessages.slice(0, 4)
    }

    return content.trim();
}

// Fonction pour afficher la réponse de ChatGPT
function displayChatGPTResponse(response) {

    const chatHistory = document.getElementById("chat-history");
    const responseElement = document.createElement("div");
    responseElement.classList.add("response");
    responseElement.innerHTML = `<div class="bot-message">${response}</div>`;
    chatHistory.appendChild(responseElement);
}

// Fonction pour gérer les messages entrants de l'utilisateur
async function handleUserMessage() {

    const message = inputField.value;
    prevMessages.push({"role": "user", "content": `${message}`},)
    const chatHistory = document.getElementById("chat-history");
    const userMessageElement = document.createElement("div");
    userMessageElement.classList.add("user-message");
    userMessageElement.innerHTML = `<div class="user-message-text">${message}</div>`;
    chatHistory.appendChild(userMessageElement);
    inputField.value = "";

    const response = await sendRequestToChatGPT(message);
    displayChatGPTResponse(response);
}

// Ajoutez un événement pour gérer les messages de l'utilisateur
inputField.addEventListener("keydown", (event) => {
    if (event.code === "Enter" && inputField.value !== "") {
        event.preventDefault();
        handleUserMessage();
    }
});
