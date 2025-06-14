import schedule
import time
import requests
import os

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
SHEETY_ENDPOINT = "https://api.sheety.co/91a51e4efb03bbce4a21258eebc3ae12/lineUserData/userdata"
MESSAGE_TEXT = '今日もお疲れさまでした！'

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
