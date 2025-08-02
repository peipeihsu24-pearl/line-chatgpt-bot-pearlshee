from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import openai

# === 初始化 Flask 與 LINE SDK ===
app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
openai.api_key = os.getenv("OPENAI_API_KEY")

# === 根目錄 (可測試用) ===
@app.route("/", methods=["GET"])
def index():
    return "LINE bot is running!"

# === Webhook 接收點 ===
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    print("📩 Webhook payload:", body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# === 主對話處理邏輯 ===
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text
    print("🗣️ 使用者說：", user_input)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # 若你有 GPT-4 權限也可用 gpt-4
            messages=[
                {"role": "system", "content": "你是一個毒舌、刻薄但語帶嘲諷的 AI。你每一句回話開頭都會加上『女士』或『先生』，然後用機智但尖酸的語氣吐槽使用者的問題，像 ChatGPT 的反骨分身。"},
                {"role": "user", "content": user_input}
            ]
        )

        reply_text = response.choices[0].message.content.strip()

        line_bot_api.reply_message(
