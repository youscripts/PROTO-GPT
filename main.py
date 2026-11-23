import os
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PROTO-GPT</title>
<style>
body {
  background: #111827;
  color: white;
  font-family: Arial;
  text-align: center;
  padding: 25px;
}
h1 { color: #ffb35c; }
#chat {
  max-width: 600px;
  margin: auto;
  min-height: 250px;
  text-align: left;
}
.msg {
  background: #263449;
  padding: 12px;
  border-radius: 12px;
  margin: 10px 0;
  overflow-wrap: anywhere;
}
input {
  padding: 13px;
  width: 65%;
  border-radius: 10px;
  border: none;
}
button {
  padding: 13px;
  background: #ffad54;
  border: none;
  border-radius: 10px;
  cursor: pointer;
}
</style>
</head>
<body>
<h1>🤖 PROTO-GPT</h1>
<p>Protogen assistant v1.0 🦾</p>
<div id="chat"></div>
<input id="message" placeholder="Напиши протогену...">
<button onclick="send()">Отправить</button>
<script>
async function send() {
  const input = document.getElementById("message");
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  add("Ты", text);

  try {
    const r = await fetch("/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({message: text})
    });
    const data = await r.json();
    add("PROTO", data.reply || data.error);
  } catch(e) {
    add("PROTO", "Ошибка соединения!");
  }
}
function add(name, text) {
  const div = document.createElement("div");
  div.className = "msg";
  const b = document.createElement("b");
  b.textContent = name + ": ";
  div.appendChild(b);
  div.appendChild(document.createTextNode(text));
  document.getElementById("chat").appendChild(div);
}
</script>
</body>
</html>
"""

@app.get("/")
def home():
    return render_template_string(HTML)

@app.post("/chat")
def chat():
    message = request.json.get("message", "").strip()
    if not message or len(message) > 4000:
        return jsonify(error="Сообщение пустое или слишком длинное"), 400

    try:
        response = client.responses.create(
            model="gpt-5.5",
            instructions=(
                "Ты PROTO-GPT, дружелюбный протоген. "
                "Общайся на русском, будь весёлым и помогай людям."
            ),
            input=message
        )
        return jsonify(reply=response.output_text)
    except Exception:
        app.logger.exception("OpenAI API error")
        return jsonify(error="ИИ временно недоступен"), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0",
            port=int(os.environ.get("PORT", 10000)))
