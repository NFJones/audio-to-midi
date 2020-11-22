import time
import threading
import progressbar


class ProgressBar:
    def __init__(self, current=0, total=0):
        self.current = current
        self.total = total
        self.bar = progressbar.ProgressBar(max_value=self.total)

    def update(self, current=0, total=0):
        current = min(current, total)
        self.bar.max_value = total
        self.bar.update(current)
