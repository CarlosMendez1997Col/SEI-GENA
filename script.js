const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

function addMessage(role, content) {
    const isBot = role === 'bot';
    const div = document.createElement('div');
    div.className = `message ${isBot ? 'bot-msg' : 'user-msg'}`; 
    div.innerHTML = `<strong>${isBot ? 'IA' : 'Tú'}:</strong> ${content}`;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
    return div; // DEVOLVEMOS EL DIV para poder editarlo luego
}

async function enviarPregunta() {
    const texto = userInput.value.trim();
    if (!texto) return;

    // Añadimos mensaje del usuario
    addMessage('user', texto);
    userInput.value = '';

    // Añadimos el mensaje de carga y guardamos su referencia
    const botMsgDiv = addMessage('bot', '<i>Procesando respuesta con Phi-3...</i>');

    try {
        const response = await fetch('https://nonmultiplicational-van-nondualistic.ngrok-free.dev/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pregunta: texto })
        });

        if (!response.ok) throw new Error("Error en el servidor");

        const data = await response.json();
        
        // REEMPLAZAMOS EL CONTENIDO del div que guardamos antes
        if (data.respuesta) {
            botMsgDiv.innerHTML = `<strong>IA:</strong> ${data.respuesta}<br><br><small style="color: gray;">📌 Fuente: ${data.titulo} (${data.institucion})</small>`;
        } else {
            botMsgDiv.innerHTML = "<strong>IA:</strong> Error: El servidor no envió una respuesta válida.";
        }

    } catch (error) {
        console.error("Error:", error);
        botMsgDiv.innerHTML = "<strong>IA:</strong> ❌ Error de conexión. Revisa que el túnel Ngrok esté online.";
        botMsgDiv.classList.add('error-msg'); // Opcional: clase CSS para ponerlo en rojo
    }
}

sendBtn.addEventListener('click', enviarPregunta);
userInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') enviarPregunta(); });
