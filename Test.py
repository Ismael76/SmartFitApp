import schedule
import time

def job():
    print("Hello")
    return

schedule.every().day.at("00:53").do(job)

while True:
    schedule.run_pending()