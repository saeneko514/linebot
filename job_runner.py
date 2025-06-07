from bs4 import BeautifulSoup
import requests
import os
from linebot import LineBotApi
from linebot.models import TextSendMessage

# LINE設定
# CHANNEL_ACCESS_TOKEN = os.environ.get('CHANNEL_ACCESS_TOKEN')
# USER_ID = os.environ.get('USER_ID')
CHANNEL_ACCESS_TOKEN ="f5wyS1nU1GG2Tob2zmEGMaQQnWYpN+FBpUsw2rgK5FN2P/ZfnmWnsthJm7wLKH0cLEq/khxpEQwCxl55MgeVa/A83qlVDTbiZdi2yVSNtCAJzC42A6PAqkYELgXWX9cQ8n04zJa+aT2SIdrSFWfSygdB04t89/1O/w1cDnyilFU="
USER_ID = "U8ccba01578d82755c5bc76117b020dd7"
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)


# Sheety設定
SHEETY_ID = "91a51e4efb03bbce4a21258eebc3ae12"
SHEETY_ENDPOINT = f"https://api.sheety.co/{SHEETY_ID}/貸借取引情報リスト/シート1"

def load_urls_from_sheety():
    response = requests.get(SHEETY_ENDPOINT)
    data = response.json()
    print("API Response:", data)  # ← これで構造を確認できる

    # データキーを正確に指定（例: data["シート1"]）
    sheet_key = "シート1"  # Sheetyのレスポンスキー名
    urls = [entry["url"] for entry in data[sheet_key] if entry.get("url")]
    return urls

# 関数を実行して結果を表示
urls = load_urls_from_sheety()
print("取得したURL一覧:", urls)

# 指定URLから株式情報をスクレイピング
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

# LINEへ送信
def send_line_message(stock_data):
    message = "\n".join([f"{key}: {value}" for key, value in stock_data.items()])
    line_bot_api.push_message(USER_ID, TextSendMessage(text=message))

# メイン処理
def job():
    urls = load_urls_from_sheety()
    for url in urls:
        stock_info = fetch_stock_info(url)
        send_line_message(stock_info)

if __name__ == "__main__":
    job()