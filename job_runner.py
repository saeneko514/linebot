from main import job
import schedule
import time

# 定期実行設定
schedule.every().day.at("00:16").do(job)  # JST 9:16 → UTC 0:16

while True:
    schedule.run_pending()
    time.sleep(1)