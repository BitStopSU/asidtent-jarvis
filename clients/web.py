"""
JARVIS - Web Client
Веб-интерфейс (чат + файлы + профиль)
"""
from flask import Flask, render_template_string, request, jsonify
import requests


app = Flask(__name__)

SERVER_URL = "http://localhost:5001"


HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>JARVIS</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    background: #0a0e17; color: #fff;
    font-family: 'Segoe UI', Arial;
    height: 100vh; display: flex;
    justify-content: center; align-items: center;
}
.container {
    width: 800px; max-width: 95%;
    background: #1a1f2e;
    border-radius: 15px; padding: 30px;
}
h1 { color: #00d2ff; text-align: center; margin-bottom: 20px; }
#chat {
    height: 400px; overflow-y: auto;
    background: #0f1419; border-radius: 10px;
    padding: 20px; margin-bottom: 15px;
}
.msg { margin-bottom: 10px; padding: 10px;
    border-radius: 8px; max-width: 80%; }
.user { background: #0078d4; margin-left: auto; }
.jarvis { background: #2a3040; }
.input-area { display: flex; gap: 10px; }
input {
    flex: 1; padding: 15px; border-radius: 8px;
    border: none; background: #0f1419;
    color: #fff; font-size: 15px;
}
button {
    padding: 15px 25px; border-radius: 8px;
    border: none; background: #00d2ff;
    color: #000; font-weight: bold;
    cursor: pointer;
}
button:hover { background: #00b8e6; }
.status { text-align: center; margin-bottom: 15px; font-size: 13px; }
</style>
</head>
<body>
<div class="container">
    <h1>⚡ JARVIS</h1>
    <div class="status" id="status">Проверка...</div>
    <div id="chat"></div>
    <div class="input-area">
        <input id="cmd" placeholder="Введите команду..."
            onkeypress="if(event.key==='Enter') send()">
        <button onclick="send()">➤</button>
    </div>
</div>

<script>
function addMsg(text, type) {
    var chat = document.getElementById('chat');
    var div = document.createElement('div');
    div.className = 'msg ' + type;
    div.textContent = (type === 'user' ? 'Вы: ' : 'JARVIS: ') + text;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

function send() {
    var input = document.getElementById('cmd');
    var cmd = input.value.trim();
    if (!cmd) return;
    addMsg(cmd, 'user');
    input.value = '';

    fetch('/api/command', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({command: cmd})
    })
    .then(r => r.json())
    .then(d => addMsg(d.response, 'jarvis'))
    .catch(() => addMsg('Ошибка соединения', 'jarvis'));
}

function checkStatus() {
    fetch('/api/status')
        .then(r => r.json())
        .then(d => {
            document.getElementById('status').textContent =
                '✅ Сервер онлайн';
        })
        .catch(() => {
            document.getElementById('status').textContent =
                '❌ Сервер офлайн';
        });
}

checkStatus();
setInterval(checkStatus, 10000);
</script>
</body>
</html>
"""


@app.route("/")
def index():
    """Главная страница"""
    return render_template_string(HTML)


@app.route("/api/command", methods=["POST"])
def command():
    """Проксирование команды на сервер"""
    data = request.json
    cmd = data.get("command", "")

    try:
        resp = requests.post(
            f"{SERVER_URL}/api/command",
            json={"command": cmd},
            timeout=30
        )
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({"response": f"Сервер недоступен: {e}"})


@app.route("/api/status", methods=["GET"])
def status():
    """Статус сервера"""
    try:
        resp = requests.get(f"{SERVER_URL}/api/status", timeout=5)
        return jsonify(resp.json())
    except Exception:
        return jsonify({"status": "offline"})


def run(host="0.0.0.0", port=3000):
    """Запуск веб-клиента"""
    print(f"🌐 Веб-интерфейс: http://localhost:{port}")
    app.run(host=host, port=port)


if __name__ == "__main__":
    run()