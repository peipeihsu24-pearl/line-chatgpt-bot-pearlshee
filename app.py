from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from openai import OpenAI
import os

# === 初始化 Flask 與 LINE SDK ===
app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# === 初始化 OpenAI Client（新版寫法）===
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === 根目錄（測試用）===
@app.route("/", methods=["GET"])
def index():
    return "LINE bot is running!"

# === Webhook 接收點 ===
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    print("📩 Webhook payload:", body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# === 主訊息處理器 ===
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text
    print("🗣️ 使用者說：", user_input)

try:
    # comment 掉 GPT 呼叫（沒錢不能問）
    # response = client.chat.completions.create(...)
    # reply_text = response.choices[0].message.content.strip()

    # 👇 用假訊息取代
    reply_text = "（假裝我是GPT）女士，你問的這種問題，我連眼珠都懶得翻。"

except Exception as e:
    print("❌ GPT 回覆錯誤:", e, flush=True)
    reply_text = "女士/先生，我剛剛卡住了，你的問題太高深莫測了。"

# 不管怎樣都回 LINE
line_bot_api.reply_message(
    event.reply_token,
    TextSendMessage(text=reply_text)
)


# === 啟動應用（Render用） ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


     
