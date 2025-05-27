import schedule
import time
from datetime import datetime

def job_function(name):
    """실제로 수행할 작업 함수"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Hello, {name}! This job is running.")

# 1. 특정 시간마다 반복 (매일 10시 30분)
# schedule.every().day.at("10:30").do(job_function, name="Daily Report")

# 2. 특정 주기마다 반복 (매 10분마다)
# schedule.every(10).minutes.do(job_function, name="Data Sync")

# 3. 특정 요일의 특정 시간 (매주 월요일 09:00)
# schedule.every().monday.at("09:00").do(job_function, name="Weekly Cleanup")

# 4. 특정 시간마다 반복 (매 5초마다)
schedule.every(5).seconds.do(job_function, name="Quick Check")

# 스케줄러 실행 루프
print("Scheduler started. Press Ctrl+C to exit.")
while True:
    schedule.run_pending() # 현재 시간이 되면 실행해야 할 작업을 실행
    time.sleep(1) # 1초마다 확인