const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

function addMessage(role, content) {
    const isBot = role === 'bot';
    const div = document.createElement('div');
    div.className = `message ${isBot ? 'bot-msg' : 'user-msg'}`; 
    // Nota: Asegúrate de tener clases básicas en tu CSS para verlos, 
    // o usa el innerHTML que tenías antes si prefieres el diseño.
    div.innerHTML = `<strong>${isBot ? 'IA' : 'Tú'}:</strong> ${content}`;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function enviarPregunta() {
    const texto = userInput.value.trim();
    if (!texto) return;

    addMessage('user', texto);
    userInput.value = '';
    addMessage('bot', 'Procesando respuesta...');

    try {
        const response = await fetch('https://nonmultiplicational-van-nondualistic.ngrok-free.dev/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pregunta: texto }) // VARIABLE ÚNICA: pregunta
        });

        const data = await response.json();
        
        // REEMPLAZAR EL "Procesando..." con la respuesta real
        const messages = document.querySelectorAll('.message');
        const lastMsg = messages[messages.length - 1];
        
        if (data.respuesta) {
            lastMsg.innerHTML = `<strong>IA:</strong> ${data.respuesta}<br><small>Ref: ${data.titulo}</small>`;
        } else {
            lastMsg.innerHTML = "Error: El servidor no envió texto.";
        }

    } catch (error) {
        console.error("Error:", error);
        addMessage('bot', "Error de conexión con el servidor.");
    }
}

sendBtn.addEventListener('click', enviarPregunta);
userInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') enviarPregunta(); });
