
const chatBox = document.getElementById("chatBox");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const guardrailStatus = document.getElementById("guardrailStatus");
const clearBtn = document.getElementById("clearBtn");


// Check whether HTML elements are connected
if (!chatBox || !userInput || !sendBtn || !guardrailStatus || !clearBtn) {
    console.error("Error: One or more HTML elements are missing.");
}


// Add message to chat
function addMessage(message, sender) {

    const messageDiv = document.createElement("div");
    messageDiv.className = "message " + sender;

    const avatar = document.createElement("div");
    avatar.className = "avatar";

    avatar.textContent = sender === "user" ? "👤" : "🛡️";

    const bubble = document.createElement("div");
    bubble.className = "bubble";

    bubble.textContent = message;

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(bubble);

    chatBox.appendChild(messageDiv);

    chatBox.scrollTop = chatBox.scrollHeight;
}


// Send message to AI agent
async function sendMessage() {

    const message = userInput.value.trim();

    // Prevent empty messages
    if (!message) {
        return;
    }

    console.log("User message:", message);

    // Display user message
    addMessage(message, "user");

    // Clear input
    userInput.value = "";

    // Disable button while processing
    sendBtn.disabled = true;
    sendBtn.textContent = "Processing...";

    guardrailStatus.textContent = "⏳ Sending request...";
    guardrailStatus.classList.remove("blocked");

    try {

        // Send request to Flask backend
        const response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: message
            })

        });

        console.log("HTTP Status:", response.status);

        // Read server response
        const data = await response.json();

        console.log("Server response:", data);

        // Handle HTTP errors
        if (!response.ok) {

            throw new Error(
                data.error || "Server error: " + response.status
            );

        }

        // Display AI response
        if (data.response) {

            addMessage(data.response, "bot");

        } else {

            addMessage(
                "The AI agent returned an empty response.",
                "bot"
            );

        }

        // Update guardrail status
        if (data.success === true) {

            guardrailStatus.textContent =
                "🛡️ Guardrails passed successfully";

            guardrailStatus.classList.remove("blocked");

        } else {

            guardrailStatus.textContent =
                "⚠️ " + (data.guardrail || data.error || "Request blocked");

            guardrailStatus.classList.add("blocked");

        }

    }

    catch (error) {

        console.error("Request failed:", error);

        addMessage(
            "Error: " + error.message,
            "bot"
        );

        guardrailStatus.textContent =
            "⚠️ Connection error";

        guardrailStatus.classList.add("blocked");

    }

    finally {

        // Enable button again
        sendBtn.disabled = false;

        sendBtn.textContent = "Send ➤";

        userInput.focus();

    }

}


// Send button click event
sendBtn.addEventListener("click", function() {

    console.log("Send button clicked");

    sendMessage();

});


// Send using Enter key
userInput.addEventListener("keydown", function(event) {

    if (event.key === "Enter" && !event.shiftKey) {

        event.preventDefault();

        if (!sendBtn.disabled) {

            console.log("Enter key pressed");

            sendMessage();

        }

    }

});


// Clear conversation
clearBtn.addEventListener("click", function() {

    chatBox.replaceChildren();

    addMessage(
        "Hello! I am your AI agent. How can I help you today?",
        "bot"
    );

    guardrailStatus.textContent =
        "🛡️ Guardrails are active";

    guardrailStatus.classList.remove("blocked");

    userInput.value = "";

    userInput.focus();

});


// Initial welcome message
if (chatBox.children.length === 0) {

    addMessage(
        "Hello! I am your AI agent. How can I help you today?",
        "bot"
    );

}

console.log("AI Chat JavaScript loaded successfully.");
