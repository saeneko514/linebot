import schedule
import time
from job_project_a import job_project_a
# from job_project_b import job_project_b 

# スケジュール設定（日本時間-9時間）
schedule.every().day.at("02:45").do(job_project_a)
# schedule.every().day.at("03:00").do(job_project_b)

if __name__ == "__main__":
    print("Scheduler started.")
    while True:
        schedule.run_pending()
        time.sleep(60)
