from datetime import time

import schedule


def myjob():
    print('hello')


def job():
    print('time......')


schedule.every(5).seconds.do(myjob)
schedule.every(10).seconds.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)