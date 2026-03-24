const sidebarLeft = document.getElementById('sidebar');
const sidebarRight = document.getElementById('inspector-sidebar');
const toggleLeftBtn = document.getElementById('toggle-sidebar');
const toggleRightBtn = document.getElementById('toggle-inspector');
const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const inputWrapper = document.getElementById('input-wrapper');
const sendBtn = document.getElementById('send-btn');
const inspectorContent = document.getElementById('inspector-content');

// --- Eventos de UI ---
toggleLeftBtn.addEventListener('click', () => sidebarLeft.classList.toggle('collapsed'));
toggleRightBtn.addEventListener('click', () => sidebarRight.classList.toggle('collapsed'));
userInput.addEventListener('focus', () => inputWrapper.classList.add('input-container-focus'));
userInput.addEventListener('blur', () => inputWrapper.classList.remove('input-container-focus'));

// --- Función para añadir mensajes al chat ---
function addMessage(role, content, id = null) {
    const isBot = role === 'bot';
    const wrapper = document.createElement('div');
    wrapper.className = `flex gap-4 animate-fade-in ${!isBot ? 'flex-row-reverse' : ''}`;
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

// --- Función para actualizar el panel de Inspector ---
function updateInspector(titulo, institucion, resumen) {
    inspectorContent.innerHTML = `
        <div class="space-y-6 animate-fade-in">
            <div class="bg-slate-900/50 border border-slate-800 p-4 rounded-xl">
                <p class="text-[10px] uppercase tracking-widest text-slate-500 mb-1">Título de Licitación</p>
                <p class="text-sm font-semibold text-slate-200">${titulo}</p>
            </div>
            <div class="bg-slate-900/50 border border-slate-800 p-4 rounded-xl">
                <p class="text-[10px] uppercase tracking-widest text-slate-500 mb-1">Institución</p>
                <p class="text-sm text-green-400">${institucion}</p>
            </div>
            <div class="bg-green-900/10 border border-green-900/30 p-4 rounded-xl">
                <p class="text-[10px] uppercase tracking-widest text-green-500 mb-1">Resumen de Análisis</p>
                <p class="text-xs leading-relaxed text-slate-300 italic">"${resumen}"</p>
            </div>
        </div>
    `;
}

// --- Lógica Principal de Envío y Consulta ---
async function handleAction() {
    const query = userInput.value.trim();
    if (!query) return;

    // 1. Mostrar mensaje del usuario
    addMessage('user', query);
    userInput.value = '';

    // 2. Crear burbuja de carga del bot
    const botMsgId = 'bot-' + Date.now();
    addMessage('bot', '<i class="fas fa-spinner fa-spin mr-2"></i> Analizando pliegos...', botMsgId);

    try {
        // 3. Petición al backend en GCP
        const response = await fetch('https://nonmultiplicational-van-nondualistic.ngrok-free.dev/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_question: query })
        });

        if (!response.ok) throw new Error("Error en la respuesta del servidor");

        const data = await response.json();
        
        // 4. Buscar la burbuja del bot para reemplazar el texto
        const botWrapper = document.getElementById(botMsgId);
        const botDiv = botWrapper.querySelector('.message-content');

        if (data.response) {
            botDiv.innerHTML = data.response;
            updateInspector(
                data.metadata.titulo || "Licitación detectada", 
                data.metadata.institucion || "Institución analizada", 
                "Análisis de licitación completado con éxito."
            );
        }
    } catch (error) {
        console.error("Error:", error);
        const botWrapper = document.getElementById(botMsgId);
        if (botWrapper) {
            const botDiv = botWrapper.querySelector('.message-content');
            botDiv.innerHTML = '<span class="text-red-400"><i class="fas fa-exclamation-triangle mr-2"></i> Error de conexión con SEI-GENA. Revisa si el contenido no seguro está permitido en el navegador.</span>';
        }
    }
}

// --- Listeners de Envío ---
sendBtn.addEventListener('click', handleAction);
userInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') handleAction(); });

// --- Reloj de Colombia ---
const timeDisplay = document.getElementById('colombia-time');
if (timeDisplay) {
    setInterval(() => {
        timeDisplay.textContent = new Intl.DateTimeFormat('es-CO', {
            timeZone: 'America/Bogota', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true
        }).format(new Date());
    }, 1000);
}