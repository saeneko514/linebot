import schedule
import time
import requests
import os

SHEETY_ID = os.environ["SHEETY_ID"]
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
SHEETY_ENDPOINT = f"https://api.sheety.co/{SHEETY_ID}/新しい自己肯定感スコアアプリ測定結果/useragreement"
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

    user_list = data.get("useragreement", [])
    user_ids = [entry["userId"] for entry in user_list if "userId" in entry]
    return user_ids


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
