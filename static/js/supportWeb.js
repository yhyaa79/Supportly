export function supporterWeb(nameWeb, linkWeb, model) {

    /*     
    The first time you use this library, you must wait a few minutes 
    after logging in for the sitemap to be downloaded and saved on the server, 
    and the next time it will be ready to ask questions without delay.
    */

    // nameWeb: your website name 
    // linkWeb: your website link 
    // model:'gpt-3.5-turbo', 'gemma-3-12b-it', 'llama-3.1-70b-instruct' ...


    // Create style
    const style = document.createElement('style');
    style.textContent = `
        .chat-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.75); display: flex; justify-content: center;
            align-items: center; z-index: 9999; opacity: 0; visibility: hidden;
            transition: opacity 0.4s ease, visibility 0.4s ease;
        }
        .chat-overlay.show { opacity: 1; visibility: visible; }

        .chat-modal {
            background: #ffffff; width: 90%; max-width: 480px; height: 80vh;
            max-height: 700px; border-radius: 20px; overflow: hidden;
            box-shadow: 0 25px 70px rgba(0,0,0,0.35);
            display: flex; flex-direction: column;
            transform: scale(0.7); transition: transform 0.4s ease;
        }
        .chat-overlay.show .chat-modal { transform: scale(1); }

        .chat-header {
            background: linear-gradient(135deg, #5e35b1, #7e57c2);
            color: white; padding: 18px 20px; text-align: center;
            position: relative; font-family: sans-serif;
        }
        .chat-header h2 {
            margin: 0; font-size: 1.4rem; font-weight: 600;
        }
        .close-chat {
            position: absolute; top: 50%; right: 20px;
            transform: translateY(-50%); background: rgba(255,255,255,0.2);
            border: none; color: white; width: 36px; height: 36px;
            border-radius: 50%; font-size: 1.5rem; cursor: pointer;
            backdrop-filter: blur(5px);
        }
        .close-chat:hover { background: rgba(255,255,255,0.3); }

        .chat-messages {
            flex: 1; padding: 20px; overflow-y: auto;
            background: #f5f5f5; display: flex; flex-direction: column;
            gap: 14px; font-family: sans-serif;
        }
        .message {
            max-width: 80%; padding: 12px 16px; border-radius: 18px;
            line-height: 1.5; word-wrap: break-word; font-size: 0.95rem;
        }
        .message.user {
            align-self: flex-end; background: #5e35b1; color: white;
            border-bottom-right-radius: 4px;
        }
        .message.ai {
            align-self: flex-start; background: white; color: #333;
            border: 1px solid #eee; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-bottom-left-radius: 4px;
        }
        .typing {
            font-style: italic; color: #888; font-size: 0.9rem;
        }

        .chat-input-area {
            padding: 16px; background: white; border-top: 1px solid #eee;
            display: flex; gap: 10px; align-items: center;
        }
        .chat-input {
            flex: 1; padding: 14px 18px; border: 1px solid #ddd;
            border-radius: 50px; outline: none; font-size: 1rem;
            transition: border 0.3s;
        }
        .chat-input:focus {
            border-color: #5e35b1; box-shadow: 0 0 0 3px rgba(94,53,177,0.15);
        }
        .send-btn {
            background: #5e35b1; color: white; border: none;
            width: 46px; height: 46px; border-radius: 50%;
            cursor: pointer; font-size: 1.3rem;
            display: flex; align-items: center; justify-content: center;
            transition: 0.3s;
        }
        .send-btn:hover { background: #4a278c; transform: scale(1.1); }
        .send-btn:disabled { opacity: 0.5; cursor: not-allowed; }
    `;
    document.head.appendChild(style);

    // Create modal
    const overlay = document.createElement('div');
    overlay.className = 'chat-overlay';
    overlay.innerHTML = `
        <div class="chat-modal">
            <div class="chat-header">
                <h2>پشتیبان ${nameWeb}</h2>
                <button class="close-chat">×</button>
            </div>
            <div class="chat-messages" id="messages">
                <div class="message ai">
                    Hello! How can I help you? 😊
                </div>
            </div>
            <div class="chat-input-area">
                <input type="text" class="chat-input" placeholder="Write your message..." id="userInput">
                <button class="send-btn" id="sendBtn">➤</button>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);

    // modal display
    setTimeout(() => overlay.classList.add('show'), 100);

    // Elements
    const messagesContainer = overlay.querySelector('#messages');
    const userInput = overlay.querySelector('#userInput');
    const sendBtn = overlay.querySelector('#sendBtn');
    const closeBtn = overlay.querySelector('.close-chat');

    // Add message function
    function addMessage(text, type) {
        const msg = document.createElement('div');
        msg.className = `message ${type}`;
        msg.textContent = text;
        messagesContainer.appendChild(msg);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Send a request to the API to check and create a sitemap on the server
    async function toOpen() {
        try {
            const response = await fetch('http://127.0.0.1:8000/str', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    linkWeb
                })
            });

            const data = await response.json();

        } catch (err) {
            addMessage('The connection to the server was lost.', 'ai');
            console.error(err);
        }
    }



    // Send message to api
    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        addMessage(text, 'user');
        userInput.value = '';

        const typing = document.createElement('div');
        typing.className = 'message ai typing';
        typing.textContent = 'Typing...';
        messagesContainer.appendChild(typing);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        try {
            // Send user messages and receive bot messages from API
            const response = await fetch('http://127.0.0.1:8000/run', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    linkWeb: linkWeb,
                    model: model
                })
            });

            typing.remove();

            if (!response.ok) {
                const errorText = await response.text();
                addMessage(`خطا: ${response.status} — ${errorText}`, 'ai');
                return;
            }

            const data = await response.json();

            if (data.result) {
                addMessage(data.result, 'ai');
            } else {
                addMessage('No response received!', 'ai');
            }

        } catch (err) {
            typing.remove();
            addMessage('The connection to the server was lost.', 'ai');
            console.error('Network error:', err);
        }
    }


    toOpen()

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', e => {
        if (e.key === 'Enter') sendMessage();
    });

    // Close modal
    function closeModal() {
        overlay.classList.remove('show');
        setTimeout(() => overlay.remove(), 400);
    }
    closeBtn.addEventListener('click', closeModal);
    overlay.addEventListener('click', e => {
        if (e.target === overlay) closeModal();
    });

    // Autofocus on input
    setTimeout(() => userInput.focus(), 500);
}