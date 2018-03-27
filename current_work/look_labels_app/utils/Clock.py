import time


class Clock(object):
    """用来控制调用不至于过度频繁的计时器"""

    def __init__(self, min_tick_interval=0.1):
        self.last_tick = time.time()
        self.interval = min_tick_interval

    def tick(self):
        now = time.time()
        if now - self.last_tick < self.interval:
            return False
        else:
            self.last_tick = now
            return True
