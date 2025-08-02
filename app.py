from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

@app.route("/", methods=['GET'])
def index():
    return "LINE bot is running!"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("⚡️ 收到使用者訊息:", event.message.text)
    reply = "你剛說了：" + event.message.text
    try:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply))
    except Exception as e:
        print("❌ reply_message 錯誤:", e)

if __name__ == "__main__":
    app.run()
