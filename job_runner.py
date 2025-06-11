from bs4 import BeautifulSoup
import requests
import os
import time
import schedule
from linebot import LineBotApi
from linebot.models import TextSendMessage

# LINE設定（Renderの環境変数で設定する）
CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
USER_ID = os.environ.get("USER_ID")
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

print(f"通知対象のユーザーID: {USER_ID}")


# Sheety設定
SHEETY_ID = os.environ.get("SHEETY_ENDPOINT")
SHEETY_ENDPOINT = f"https://api.sheety.co/{SHEETY_ID}/貸借取引情報リスト/sheet1"

def load_urls_from_sheety():
    response = requests.get(SHEETY_ENDPOINT)
    data = response.json()
    print(data)  # ← デバッグ用に Sheet API のレスポンス確認

    # ① Sheety APIのクォータ制限チェック
    if "errors" in data:
        print("❌ Sheety APIエラー:", data["errors"])
        return []

    # ② sheet1 キーが存在するかチェック
    sheet_key = "sheet1"
    if sheet_key not in data:
        print(f"❌ '{sheet_key}' がレスポンスに見つかりません。レスポンス: {data}")
        return []

    # ③ url カラムが存在する行だけを抽出
    urls = [entry["url"] for entry in data[sheet_key] if entry.get("url")]
    return urls

# def load_urls_from_sheety():
#     response = requests.get(SHEETY_ENDPOINT)
#     data = response.json()
#     print(data)
#     sheet_key = "sheet1"
#     urls = [entry["url"] for entry in data[sheet_key] if entry.get("url")]
#     return urls

def fetch_stock_info(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    result = {}
    try:
        result["銘柄名"] = soup.find('h1', class_="heading__ttl").get_text(strip=True)
    except:
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
    urls = load_urls_from_sheety()
    for url in urls:
        stock_info = fetch_stock_info(url)
        send_line_message(stock_info)

# 通知したい時間-9時間
schedule.every().day.at("04:30").do(job)

if __name__ == "__main__":
    print("Worker started. Waiting for schedule...")
    while True:
        schedule.run_pending()
        time.sleep(60)
