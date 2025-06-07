from bs4 import BeautifulSoup
import requests
import os
from linebot import LineBotApi
from linebot.models import TextSendMessage

# LINE設定
CHANNEL_ACCESS_TOKEN = os.environ.get('CHANNEL_ACCESS_TOKEN')
USER_ID = os.environ.get('USER_ID')
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

# URLリストファイル
URL_FILE = "stock_urls.txt"

def load_urls():
    if not os.path.exists(URL_FILE):
        return []
    with open(URL_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

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
    urls = load_urls()
    for url in urls:
        stock_info = fetch_stock_info(url)
        send_line_message(stock_info)

if __name__ == "__main__":
    job()
