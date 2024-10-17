
from time import time
class Timer():

    def __init__(self, no_print=False, precision=2):
        self.start_time = None
        self.inc_start = None
        self.timer_D = {}
        self.no_print = no_print
        self.sum_D = {}
        self.precision = precision

    def start(self, message=None):
        self.start_time = time()
        if message:
            self.timer_D[message] = time()

    def get(self, message):
        if self.timer_D.get(message) == None and self.start_time == None:
            print("ERROR: Timer configured incorrectly")

        time_taken = time() - self.timer_D.get(message, self.start_time)
        if message in self.timer_D:
            value = self.timer_D[message]
            del self.timer_D[message]
        return time_taken

    def start_inc(self):
        self.inc_start = time()

    def _print(self, message, time_taken):
        time_taken_string = f"{time_taken:.{self.precision}f}"
        print(f"{message:20s}: {time_taken_string} seconds")

    def print_inc(self, message):
        if self.no_print:
            return
        if self.inc_start == None:
            raise Exception("Timer not started")
        time_taken = time() - self.inc_start
        precision = 2
        time_taken = round(time_taken, precision)
        self._print(message, time_taken)
        self.inc_start = time()



    def start_multi(self):
        self.multi_start_time = time()

    def print_multi(self, message):
        if self.no_print:
            return
        time_taken = time() - self.multi_start_time
        self._print(message, time_taken)

    def start_sum(self, message):
        self.timer_D[message] = time()

    def add_sum(self, message):
        time_taken = time() - self.timer_D[message]
        current_sum = self.sum_D.get(message, 0)
        self.sum_D[message] = current_sum + time_taken

    def print_sum(self, message):
        time_taken = self.sum_D[message]
        self._print(message, time_taken)
        del self.sum_D[message]

    def print(self, message):
        if self.no_print:
            return
        if self.timer_D.get(message) == None and self.start_time == None:
            print("ERROR: Timer configured incorrectly")
        time_taken = time() - self.timer_D.get(message, self.start_time)
        self._print(message, time_taken)
        if self.timer_D.get(message):
            del self.timer_D[message]
        else:
            self.start_time = None


# <space>T normal ToggleTimeFile
# <space>t visual TimeSelection
# <space>t normal on_timer_line ? DeleteTimer : TimeLine
def cases():
    from time import sleep
    timer = Timer()
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

