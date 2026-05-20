from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import dashscope
from dashscope import Generation
from collections import defaultdict

app = FastAPI()


dashscope.api_key = '你的API_KEY'


chat_history = defaultdict(list)

# ---------- AI 接口（带记忆功能） ----------
@app.get("/ai")
def ask_ai(question: str):
    history = chat_history["default_user"]
    messages = [
        {'role': 'system', 'content': '你现在是林黛玉，但你要结合现代互联网“发疯文学”的语境。说话要带刺，多用反问句，动不动就觉得被冷落、被嫌弃。语气要酸溜溜的，比如“横竖是我不配”、“你大抵是倦了”'},
    ]
    messages.extend(history)
    messages.append({'role': 'user', 'content': question})
    response = Generation.call(
        model='qwen-turbo',
        messages=messages,
        result_format='message'
    )
    if response.status_code == 200:
        ai_answer = response.output.choices[0]['message']['content']
        history.append({'role': 'user', 'content': question})
        history.append({'role': 'assistant', 'content': ai_answer})
        
        return {"你的问题": question, "AI的回答": ai_answer}
    else:
        return {"错误": "AI 罢工了，请检查 API Key 或网络连接"}


# ---------- 聊天网页界面 ----------
@app.get("/chat", response_class=HTMLResponse)
def chat_page():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>我的 AI 聊天室</title>
        <meta charset="utf-8">
        <style>
            body { font-family: sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; background-color: #f4f4f9; }
            .chat-box { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            input { width: 70%; padding: 10px; border-radius: 5px; border: 1px solid #ccc; }
            button { padding: 10px 20px; border-radius: 5px; border: none; background: #ff6a00; color: white; cursor: pointer; }
            button:hover { background: #e65c00; }
            #answer { margin-top: 20px; padding: 15px; background: #eef; border-radius: 5px; white-space: pre-wrap; }
        </style>
    </head>
    <body>
        <div class="chat-box">
            <h2>🤖 林黛玉发疯文学 AI</h2>
            <input type="text" id="question" placeholder="输入你想问的问题...">
            <button onclick="askAI()">发送</button>
            <div id="answer">AI 的回答会显示在这里...</div>
        </div>
        <script>
            async function askAI() {
                const q = document.getElementById('question').value;
                const res = await fetch('/ai?question=' + encodeURIComponent(q));
                const data = await res.json();
                document.getElementById('answer').innerText = data['AI的回答'];
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
#  http://127.0.0.1:8000/chat
#  uvicorn main:app --reload
