
from time import time, sleep
class Timer():

    def __init__(self, no_print=False):
        self.start_time = None
        self.inc_start = None
        self.timer_D = {}
        self.no_print = no_print
        self.sum_D = {}

    def start(self, message=None):
        self.start_time = time()
        if message:
            self.timer_D[message] = time()

    def start_inc(self):
        self.inc_start = time()
    def print_inc(self, message):
        if self.no_print:
            return
        time_taken = time() - self.inc_start
        print(f"{message:20s}: {time_taken:.2f} seconds")
        self.inc_start = time()



    def start_multi(self):
        self.multi_start_time = time()

    def print_multi(self, message):
        if self.no_print:
            return
        time_taken = time() - self.multi_start_time
        print(f"{message:20s}: {time_taken:.2f} seconds")

    def start_sum(self, message):
        self.timer_D[message] = time()

    def add_sum(self, message):
        time_taken = time() - self.timer_D[message]
        current_sum = self.sum_D.get(message, 0)
        self.sum_D[message] = current_sum + time_taken

    def print_sum(self, message):
        time_taken = self.sum_D[message]
        print(f"{message:20s}: {time_taken:.2f} seconds")
        del self.sum_D[message]

    def print(self, message):
        if self.no_print:
            return
        if self.timer_D.get(message) == None and self.start_time == None:
            print("ERROR: Timer configured incorrectly")
        time_taken = time() - self.timer_D.get(message, self.start_time)
        print(f"{message:20s}: {time_taken:.2f} seconds")
        if self.timer_D.get(message):
            del self.timer_D[message]
        else:
            self.start_time = None

timer = Timer()

# <space>T normal ToggleTimeFile
# <space>t visual TimeSelection
# <space>t normal on_timer_line ? DeleteTimer : TimeLine
def cases():
    # If there are multiple lines printed, only 1 can exist at a time,
    # otherwise somewhere we'll require two arguments

    # Variant 1
    timer.start("sleep")
    sleep(1)
    timer.print("sleep")
    # --- 

    # Variant 2
    timer.start()
    sleep(1)
    timer.print("quick-sleep")
    # --- 

    # Variant 3
    timer.start_loop()
    for i in range(5):
        sleep(0.1)
        timer.add_loop()
    timer.print_loop("Loop Time")
    # --- 

    # Variant 4 (most used pattern, we have consecutive parts in a function that we want to arbitrarily break down and profile)
    timer.start_inc() # ID-less, only 1 can exist at a time, otherwise print_inc would require two arguments
    import pandas
    df = pandas
    timer.print_inc("import pandas")
    import datetime
    dt = datetime
    timer.print_inc("import datetime")
    # --- 

    # Variant 5 (should be main mode of profiling, so that other prints don’t interfere and if you have an error, you don’t care about performances)
    # Don’t interfere with other table that’s being printed
    timer.start_agg() # ID-less, only 1 can exist at a time, otherwise log would require two arguments
    sleep(0.1)
    print("Time slept for: 100 ms")
    timer.log_agg("First Sleep Time")
    sleep(0.2)
    print("Time slept for: 200 ms")
    timer.log_agg("Second Sleep Time")
    timer.print_agg()
    # --- 

