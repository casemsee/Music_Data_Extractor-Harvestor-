import schedule

class APIScheduler:
    def __init__(self):

    def scheduled_task(self):
        schedule.every(5).seconds.do(print_job)