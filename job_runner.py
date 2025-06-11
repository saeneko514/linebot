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
SHEETY_ENDPOINT = f"https://api.sheety.co/{SHEETY_ID}/貸借取引情報リスト/シート1"

def load_urls_from_sheety():
    try:
        response = requests.get(SHEETY_ENDPOINT, timeout=10)
        response.raise_for_status()
        data = response.json()

        print("Sheetyからのレスポンス:", data)

        # 最初のキーを動的に取得（例: 'sheet1', '貸借取引情報リスト' など）
        sheet_key = list(data.keys())[0]
        urls = [entry["url"] for entry in data[sheet_key] if entry.get("url")]
        return urls
    except Exception as e:
        print(f"Sheetyデータ取得エラー: {e}")
        return []

def fetch_stock_info(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
    except Exception as e:
        return {"エラー": f"URL取得失敗: {e}", "URL": url}

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

    result["URL"] = url
    return result

def send_line_message(stock_data):
    message = "\n".join([f"{key}: {value}" for key, value in stock_data.items()])
    try:
        line_bot_api.push_message(USER_ID, TextSendMessage(text=message))
        print("LINE通知成功:", message)
    except Exception as e:
        print("LINE通知エラー:", e)

def job():
    print("job() 関数が呼び出されました")  # ← 追加
    urls = load_urls_from_sheety()
    if not urls:
        print("URLが取得できなかったため、通知をスキップします")
        return

    for url in urls:
        stock_info = fetch_stock_info(url)
        send_line_message(stock_info)

# 通知したい時間（JST 11:45 → UTC 02:45）
schedule.every().day.at("03:25").do(job)

if __name__ == "__main__":
    print("Worker started. Waiting for schedule...")

    # テスト用に1回だけ即実行（確認後はコメントアウトしてOK）
    job()

    while True:
        schedule.run_pending()
        time.sleep(60)



# from bs4 import BeautifulSoup
# import requests
# import os
# import time
# import schedule
# from linebot import LineBotApi
# from linebot.models import TextSendMessage

# # LINE設定（Renderの環境変数で設定する）
# CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
# USER_ID = os.environ.get("USER_ID")
# line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

# print(f"通知対象のユーザーID: {USER_ID}")


# # Sheety設定
# SHEETY_ID = os.environ.get("SHEETY_ENDPOINT")
# SHEETY_ENDPOINT = f"https://api.sheety.co/{SHEETY_ID}/貸借取引情報リスト/シート1"

# def load_urls_from_sheety():
#     response = requests.get(SHEETY_ENDPOINT)
#     data = response.json()
#     sheet_key = "シート1"
#     urls = [entry["url"] for entry in data[sheet_key] if entry.get("url")]
#     return urls

# def fetch_stock_info(url):
#     r = requests.get(url)
#     soup = BeautifulSoup(r.content, "html.parser")
#     result = {}
#     try:
#         result["銘柄名"] = soup.find('h1', class_="heading__ttl").get_text(strip=True)
#     except:
#         result["銘柄名"] = "取得失敗"

#     fields = {
#         "差引残高": 1,
#         "品貸料率": 2,
#         "応札ランク": 2,
#         "制限措置": 1
#     }

#     for label, td_index in fields.items():
#         th = soup.find('th', string=lambda x: x and label in x)
#         if th:
#             tr = th.find_parent("tr")
#             tds = tr.find_all("td")
#             if len(tds) > td_index:
#                 result[label] = tds[td_index].text.strip()
#             else:
#                 result[label] = "取得失敗"
#         else:
#             result[label] = "該当項目なし"

#     return result

# def send_line_message(stock_data):
#     message = "\n".join([f"{key}: {value}" for key, value in stock_data.items()])
#     line_bot_api.push_message(USER_ID, TextSendMessage(text=message))

# def job():
#     urls = load_urls_from_sheety()
#     for url in urls:
#         stock_info = fetch_stock_info(url)
#         send_line_message(stock_info)

# # 通知したい時間-9時間
# schedule.every().day.at("03:15").do(job)

# if __name__ == "__main__":
#     print("Worker started. Waiting for schedule...")
#     while True:
#         schedule.run_pending()
#         time.sleep(60)
