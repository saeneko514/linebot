from flask import Flask, request
from bs4 import BeautifulSoup
import requests
import schedule
import threading
import time
import os

from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# LINE設定
CHANNEL_ACCESS_TOKEN = 'f5wyS1nU1GG2Tob2zmEGMaQQnWYpN+FBpUsw2rgK5FN2P/ZfnmWnsthJm7wLKH0cLEq/khxpEQwCxl55MgeVa/A83qlVDTbiZdi2yVSNtCAJzC42A6PAqkYELgXWX9cQ8n04zJa+aT2SIdrSFWfSygdB04t89/1O/w1cDnyilFU='
CHANNEL_SECRET =  'bf92425416b56cce6a3964cada5e18ac'
USER_ID = 'U8ccba01578d82755c5bc76117b020dd7'
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


# ==== URLリストの保存先 ====
URL_FILE = "stock_urls.txt"

def load_urls():
    if not os.path.exists(URL_FILE):
        return []
    with open(URL_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

def add_url(url):
    urls = load_urls()
    if url not in urls:
        urls.append(url)
        with open(URL_FILE, "w") as f:
            f.write("\n".join(urls) + "\n")
        return True
    return False

def fetch_stock_info(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")

    result = {}
    try:
        result["銘柄名"] = soup.find('h1', class_="heading__ttl").get_text(strip=True)
    except Exception:
        result["銘柄名"] = "取得失敗"

    fields = {
        "差引残高": 1,
        "品貸料率": 2,
        "応札ランク": 2,
        "制限措置": 1
    }

    for label, td_index in fields.items():
        th = soup.find('th', string=lambda x: x and label in x)
        if th:
            tr = th.find_parent("tr")
            tds = tr.find_all("td")
            if len(tds) > td_index:
                result[label] = tds[td_index].text.strip()
            else:
                result[label] = "取得失敗"
        else:
            result[label] = "該当項目なし"

    return result

def send_line_message(stock_data):
    message = "\n".join([f"{key}: {value}" for key, value in stock_data.items()])
    line_bot_api.push_message(USER_ID, TextSendMessage(text=message))

def job():
    urls = load_urls()
    for url in urls:
        stock_info = fetch_stock_info(url)
        send_line_message(stock_info)

# ==== 定期実行スレッド ====
def schedule_thread():
    schedule.every().day.at("08:00").do(job)  # JST 08:00 = UTC 23:00
    while True:
        schedule.run_pending()
        time.sleep(1)

# ==== Flaskアプリ ====
app = Flask(__name__)
user_states = {}

@app.route("/")
def index():
    return "LINE Bot is running!"

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    handler.handle(body, signature)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text.strip()

    if user_id in user_states:
        state = user_states.pop(user_id)
        if state == "register":
            if text.startswith("http"):
                msg = "URLを登録しました。" if add_url(text) else "すでに登録済みです。"
            else:
                msg = "URLの形式が正しくありません。"
        else:
            msg = "未対応の状態です。"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))
        return

    if text == "登録":
        user_states[user_id] = "register"
        reply = "登録したいURLを送ってください。"
    elif text == "一覧":
        urls = load_urls()
        reply = "\n".join(urls) if urls else "URLは登録されていません。"
    else:
        reply = "「登録」または「一覧」と送ってください。"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

# ==== アプリ起動 ====
if __name__ == "__main__":
    threading.Thread(target=schedule_thread, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)