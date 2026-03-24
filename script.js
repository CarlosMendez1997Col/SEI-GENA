const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const inspectorContent = document.getElementById('inspector-content');

// --- Función para añadir mensajes ---
function addMessage(role, content, id = null) {
    const isBot = role === 'bot';
    const wrapper = document.createElement('div');
    wrapper.className = `flex gap-4 animate-fade-in mb-4 ${!isBot ? 'flex-row-reverse' : ''}`;
    if (id) wrapper.setAttribute('id', id);
    
    wrapper.innerHTML = `
        <div class="w-10 h-10 rounded-xl ${isBot ? 'bg-green-900/20 border-green-500/30' : 'bg-slate-800 border-slate-700'} border flex items-center justify-center shrink-0 shadow-lg">
            <i class="fas ${isBot ? 'fa-robot text-green-500' : 'fa-user text-slate-400'} text-sm"></i>
        </div>
        <div class="message-content max-w-[80%] ${isBot ? 'bg-slate-900/50 border-slate-800' : 'bg-green-700 text-white border-green-600'} border p-4 rounded-2xl shadow-sm text-sm leading-relaxed">
            ${content}
        </div>
    `;
    chatBox.appendChild(wrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// --- Función para actualizar el Inspector ---
function updateInspector(titulo, institucion, resumen) {
    inspectorContent.innerHTML = `
        <div class="space-y-4 animate-fade-in">
            <div class="bg-slate-900/50 border border-slate-800 p-4 rounded-xl">
                <p class="text-[10px] uppercase tracking-widest text-slate-500 mb-1">Título</p>
                <p class="text-sm font-semibold text-slate-200">${titulo}</p>
            </div>
            <div class="bg-slate-900/50 border border-slate-800 p-4 rounded-xl">
                <p class="text-[10px] uppercase tracking-widest text-slate-500 mb-1">Institución</p>
                <p class="text-sm text-green-400">${institucion}</p>
            </div>
        </div>
    `;
}

// --- Lógica de Envío Sincronizada ---
async function handleAction() {
    const queryValue = userInput.value.trim();
    if (!queryValue) return;

    addMessage('user', queryValue);
    userInput.value = '';

    const botMsgId = 'bot-' + Date.now();
    addMessage('bot', '<i class="fas fa-spinner fa-spin mr-2"></i> Consultando pliegos...', botMsgId);

    try {
        const response = await fetch('https://nonmultiplicational-van-nondualistic.ngrok-free.dev/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: queryValue }) // <--- LLAVE SINCRONIZADA
        });

        if (!response.ok) throw new Error("Error en el servidor");

        const data = await response.json();
        const botWrapper = document.getElementById(botMsgId);
        const botDiv = botWrapper.querySelector('.message-content');

        if (data.response) {
            botDiv.innerHTML = data.response;
            updateInspector(data.metadata.titulo, data.metadata.institucion);
        }
    } catch (error) {
        console.error("Error:", error);
        const botWrapper = document.getElementById(botMsgId);
        if (botWrapper) {
            botWrapper.querySelector('.message-content').innerHTML = 
                '<span class="text-red-400">Error de conexión. Verifica el túnel de Ngrok.</span>';
        }
    }
}

sendBtn.addEventListener('click', handleAction);
userInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') handleAction(); });
