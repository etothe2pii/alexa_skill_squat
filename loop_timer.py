from time import time
import sys
from onepass import Wellford

class Looper:
    def __init__(self, iterable) -> None:
        self.iterable = iterable
        self.length = len(iterable)
        self.iterator = iter(iterable)
        self.current = 0

        self.time = time()
        self.average_time = Wellford()

    def __iter__(self):
        return self

    def __next__(self):
        
        self.average_time.sample(time() - self.time)

        average = self.average_time.get_x_bar()

        if average < 1:
            rate_string = f"{1/average:.3f} it/s"
        else:
            rate_string = f"{average:.3f} s/it"

        left = self.length - self.current
        time_left = left*average
        d = 0
        h = 0
        m = 0
        s = 0

        d = time_left//86400
        time_left = time_left%86400

        h = time_left//3600
        time_left = time_left%3600

        m = time_left//60
        time_left = time_left%60

        s = time_left


        print(f"{self.current/self.length*100:.2f}% [{self.current}/{self.length}] {d:.0f}:{h:.0f}:{m:.0f}:{s:.2f}, {rate_string}     ", end ="\r", file=sys.stderr)
        self.current += 1

        self.time = time()
        return self.iterator.__next__()

        
