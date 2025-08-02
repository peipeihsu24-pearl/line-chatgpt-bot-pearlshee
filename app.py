from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from openai import OpenAI
import os

# 初始化
app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Debug 模式開關
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

@app.route("/", methods=["GET"])
def index():
    return "LINE bot is running!"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text
    print("🗣️ 使用者說：", user_input)

    try:
        if DEBUG_MODE:
            reply_text = f"（假GPT）女士，你剛剛說了：『{user_input}』這麼無聊的話。"
        else:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一個毒舌、刻薄但語帶嘲諷的 AI。你每一句回話開頭都會加上『女士』或『先生』，然後用機智但尖酸的語氣吐槽使用者的問題。"
                    },
                    {
                        "role": "user",
                        "content": user_input
                    }
                ]
            )
            reply_text = response.choices[0].message.content.strip()

    except Exception as e:
        print("❌ GPT 回覆錯誤:", e, flush=True)
        reply_text = "女士/先生，我剛剛卡住了，你的問題太高深莫測了。"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)



     
