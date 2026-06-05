/**
 * IP-42-Team FAQ Chat Widget
 * Интеграция FAQ-ассистента на сайт
 */

(function() {
    // Конфигурация API
    const API_BASE = window.FAQ_WIDGET_API_BASE || 'http://localhost:8000';
    
    // Создаем контейнер для виджета
    const widgetContainer = document.createElement('div');
    widgetContainer.id = 'faq-chat-widget-container';
    
    // HTML структура виджета
    const widgetHTML = `
        <button class="faq-chat-launcher" id="faq-chat-launcher" aria-label="Открыть FAQ-ассистента">
            <span>💬</span>
        </button>

        <div class="faq-chat-widget" id="faq-chat-widget" style="display:none;">
            <div class="faq-chat-header">
                <div class="faq-chat-header-left">
                    <div class="faq-avatar">AI</div>
                    <div>
                        <div class="faq-chat-title">FAQ ассистент</div>
                        <div class="faq-chat-subtitle">Задайте вопрос о компании</div>
                    </div>
                </div>
                <button class="faq-chat-close" id="faq-chat-close" aria-label="Закрыть чат">×</button>
            </div>
            <div class="faq-chat-messages" id="faq-chat-messages"></div>
            <div class="faq-chat-footer">
                <input
                    id="faq-chat-input"
                    class="faq-chat-input"
                    placeholder="Напишите вопрос..."
                />
                <button id="faq-chat-send" class="faq-chat-send">
                    <span>➤</span>
                </button>
            </div>
        </div>
    `;
    
    // CSS стили
    const widgetStyles = `
        .faq-chat-launcher {
            position: fixed;
            bottom: 24px;
            right: 24px;
            width: 64px;
            height: 64px;
            border-radius: 999px;
            background: linear-gradient(135deg, #4f46e5, #06b6d4);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 10px 40px rgba(15, 23, 42, 0.7);
            cursor: pointer;
            border: none;
            outline: none;
            transition: transform 0.12s ease, box-shadow 0.12s ease;
            z-index: 9999;
        }

        .faq-chat-launcher:hover {
            transform: translateY(-2px);
            box-shadow: 0 16px 50px rgba(15, 23, 42, 0.9);
        }

        .faq-chat-launcher span {
            font-size: 30px;
        }

        .faq-chat-widget {
            position: fixed;
            bottom: 100px;
            right: 24px;
            width: 380px;
            max-width: calc(100vw - 32px);
            height: 500px;
            max-height: calc(100vh - 130px);
            background: #020617;
            border-radius: 24px;
            box-shadow: 0 20px 60px rgba(15, 23, 42, 0.85);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            border: 1px solid rgba(148, 163, 184, 0.25);
            backdrop-filter: blur(20px);
            z-index: 9999;
        }

        .faq-chat-header {
            padding: 14px 16px;
            background: radial-gradient(circle at top left, #4f46e5, #020617);
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: #e5e7eb;
        }

        .faq-chat-header-left {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .faq-avatar {
            width: 32px;
            height: 32px;
            border-radius: 999px;
            background: radial-gradient(circle at 30% 30%, #ffffff, #4f46e5);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            color: #020617;
            box-shadow: 0 0 0 2px rgba(15, 23, 42, 0.6);
            font-weight: bold;
        }

        .faq-chat-title {
            font-size: 14px;
            font-weight: 600;
        }

        .faq-chat-subtitle {
            font-size: 11px;
            color: #cbd5f5;
            opacity: 0.8;
        }

        .faq-chat-close {
            border: none;
            background: transparent;
            color: #e5e7eb;
            font-size: 24px;
            cursor: pointer;
            opacity: 0.8;
            line-height: 1;
            padding: 0;
        }

        .faq-chat-close:hover {
            opacity: 1;
        }

        .faq-chat-messages {
            flex: 1;
            padding: 14px 14px 10px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            overflow-y: auto;
            background: radial-gradient(circle at top, rgba(56, 189, 248, 0.05), transparent),
                        radial-gradient(circle at bottom, rgba(129, 140, 248, 0.08), #020617);
        }

        .faq-chat-message {
            max-width: 80%;
            border-radius: 14px;
            padding: 10px 14px;
            font-size: 13px;
            line-height: 1.4;
            word-wrap: break-word;
            white-space: pre-wrap;
        }

        .faq-chat-message.faq-user {
            margin-left: auto;
            background: linear-gradient(135deg, #4f46e5, #06b6d4);
            color: #e5e7eb;
            border-bottom-right-radius: 4px;
        }

        .faq-chat-message.faq-bot {
            margin-right: auto;
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid rgba(148, 163, 184, 0.3);
            color: #e5e7eb;
            border-bottom-left-radius: 4px;
        }

        .faq-chat-footer {
            padding: 10px 10px 12px;
            border-top: 1px solid rgba(30, 64, 175, 0.6);
            background: linear-gradient(to top, #020617, #020617f5);
            display: flex;
            gap: 8px;
            align-items: center;
        }

        .faq-chat-input {
            flex: 1;
            border-radius: 999px;
            border: 1px solid rgba(148, 163, 184, 0.5);
            padding: 8px 14px;
            background: rgba(15, 23, 42, 0.9);
            color: #e5e7eb;
            font-size: 13px;
            outline: none;
            font-family: 'Montserrat', sans-serif;
        }

        .faq-chat-input::placeholder {
            color: #6b7280;
        }

        .faq-chat-input:focus {
            border-color: #4f46e5;
        }

        .faq-chat-send {
            border-radius: 999px;
            border: none;
            padding: 8px 14px;
            background: linear-gradient(135deg, #4f46e5, #06b6d4);
            color: #e5e7eb;
            font-size: 13px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 4px;
            box-shadow: 0 6px 20px rgba(15, 23, 42, 0.8);
            transition: transform 0.2s;
        }

        .faq-chat-send:hover:not(:disabled) {
            transform: scale(1.05);
        }

        .faq-chat-send:disabled {
            opacity: 0.6;
            cursor: default;
            box-shadow: none;
        }

        .faq-chat-send span {
            font-size: 14px;
        }

        .faq-typing-indicator {
            display: inline-flex;
            gap: 2px;
        }

        .faq-dot {
            width: 4px;
            height: 4px;
            border-radius: 999px;
            background: #9ca3af;
            animation: faq-blink 1s infinite ease-in-out;
        }

        .faq-dot:nth-child(2) {
            animation-delay: 0.2s;
        }

        .faq-dot:nth-child(3) {
            animation-delay: 0.4s;
        }

        @keyframes faq-blink {
            0%, 80%, 100% { opacity: 0.2; transform: translateY(0); }
            40% { opacity: 1; transform: translateY(-1px); }
        }

        /* Адаптивность */
        @media (max-width: 480px) {
            .faq-chat-widget {
                width: calc(100vw - 16px);
                right: 8px;
                bottom: 90px;
            }
            
            .faq-chat-launcher {
                right: 8px;
                bottom: 16px;
                width: 56px;
                height: 56px;
            }
            
            .faq-chat-launcher span {
                font-size: 26px;
            }
        }
    `;
    
    // Добавляем стили
    const styleSheet = document.createElement('style');
    styleSheet.textContent = widgetStyles;
    document.head.appendChild(styleSheet);
    
    // Добавляем виджет в DOM
    document.body.appendChild(widgetContainer);
    widgetContainer.innerHTML = widgetHTML;
    
    // Инициализация виджета
    const launcher = document.getElementById('faq-chat-launcher');
    const widget = document.getElementById('faq-chat-widget');
    const closeBtn = document.getElementById('faq-chat-close');
    const messagesEl = document.getElementById('faq-chat-messages');
    const inputEl = document.getElementById('faq-chat-input');
    const sendBtn = document.getElementById('faq-chat-send');
    
    let isSending = false;
    
    // Функция добавления сообщения
    function appendMessage(text, from) {
        const div = document.createElement('div');
        div.className = 'faq-chat-message faq-' + from;
        div.textContent = text;
        messagesEl.appendChild(div);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }
    
    // Функция добавления индикатора набора
    function appendTyping() {
        const div = document.createElement('div');
        div.className = 'faq-chat-message faq-bot';
        div.id = 'faq-typing-indicator';
        div.innerHTML = '<div class="faq-typing-indicator"><div class="faq-dot"></div><div class="faq-dot"></div><div class="faq-dot"></div></div>';
        messagesEl.appendChild(div);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }
    
    // Удаление индикатора набора
    function removeTyping() {
        const el = document.getElementById('faq-typing-indicator');
        if (el) el.remove();
    }
    
    // Отправка сообщения
    async function sendMessage() {
        if (isSending) return;
        const text = inputEl.value.trim();
        if (!text) return;
        
        appendMessage(text, 'user');
        inputEl.value = '';
        
        isSending = true;
        sendBtn.disabled = true;
        appendTyping();
        
        try {
            const res = await fetch(API_BASE + '/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, top_k: 3 })
            });
            
            if (!res.ok) {
                throw new Error('Server error');
            }
            
            const data = await res.json();
            removeTyping();
            appendMessage(data.answer, 'bot');
        } catch (err) {
            console.error('FAQ Widget Error:', err);
            removeTyping();
            appendMessage('Не удалось получить ответ. Проверьте подключение к FAQ-серверу.', 'bot');
        } finally {
            isSending = false;
            sendBtn.disabled = false;
        }
    }
    
    // События
    launcher.addEventListener('click', () => {
        widget.style.display = 'flex';
        launcher.style.display = 'none';
        if (!messagesEl.hasChildNodes()) {
            appendMessage('Привет! Я FAQ-ассистент IP-42-Team. Задайте вопрос о нашей компании, услугах, проектах или технологиях.', 'bot');
        }
        setTimeout(() => inputEl.focus(), 50);
    });
    
    closeBtn.addEventListener('click', () => {
        widget.style.display = 'none';
        launcher.style.display = 'flex';
    });
    
    sendBtn.addEventListener('click', sendMessage);
    
    inputEl.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    console.log('IP-42-Team FAQ Widget initialized');
})();
