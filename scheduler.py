import schedule
import time
from job_project_a import job_project_a

# スケジュール設定（日本時間-9時間）
schedule.every().day.at("05:35").do(job_project_a)

if __name__ == "__main__":
    print("Scheduler started.")
    while True:
        schedule.run_pending()
        time.sleep(60)
