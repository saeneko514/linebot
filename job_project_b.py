import schedule
import time
import requests
import os

SHEETY_ID = os.environ["SHEETY_ID"]
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
SHEETY_ENDPOINT = f"https://api.sheety.co/{SHEETY_ID}/lineUserData/userdata"
DIARY_ENDPOINT = f"https://api.sheety.co/{SHEETY_ID}/lineUserData/diary"
MESSAGE_TEXT = (
    "今日もお疲れさまでした。\n"
    "今日のあなたのネガティブな感情を感じた出来事を\n"
    "５行で日記形式で書いてください。"
)

def fetch_user_ids():
    response = requests.get(SHEETY_ENDPOINT)
    print("Sheety response status:", response.status_code)
    data = response.json()
    print("Sheety response JSON:", data)
    return [row['userId'] for row in data['userdata'] if row.get('userId')]

def push_message(user_id, text):
    headers = {
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    payload = {
        'to': user_id,
        'messages': [{'type': 'text', 'text': text}]
    }
    res = requests.post('https://api.line.me/v2/bot/message/push', headers=headers, json=payload)
    print(f'Sent to {user_id}: {res.status_code}')
    print(f"Response status: {res.status_code}, body: {res.text}")

def job_project_b():
    print("Sending LINE message...")
    user_ids = fetch_user_ids()
    for user_id in user_ids:
        push_message(user_id, MESSAGE_TEXT)



@app.route("/", methods=["GET"])
def health(): return jsonify({"status": "ok"}), 200


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    message = event.message.text
    now = (datetime.utcnow() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")
    try:
        name = line_bot_api.get_profile(user_id).display_name
    except:
        name = "不明"

    data = {
        "diary": {
            "name": name,
            "userId": user_id,
            "timestamp": now,
            "diary": message
        }
    }
    requests.post(DIARY_ENDPOINT, json=data)


def send_text(user_id, text, event):
    try:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=text))
    except LineBotApiError:
        line_bot_api.push_message(user_id, TextSendMessage(text=text))


# エントリポイント
if __name__ != "__main__":
    application = app
else:
    app.run(debug=True, port=5000)
