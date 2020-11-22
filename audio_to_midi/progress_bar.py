import progressbar
import time
import threading


class ProgressBar:
    def __init__(self, current=0, total=0):
        self.current = current
        self.total = total
        self.running = False
        self.lock = threading.Lock()
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def _run(self):
        self.bar = progressbar.ProgressBar(max_value=self.total)
        while self.running:
            with self.lock:
                current = self.current
                total = self.total
            self.bar.max_value = total
            self.bar.update(current)
            time.sleep(0.1)
            if current == total:
                self.running = False

    def update(self, current=0, total=0):
        with self.lock:
            if total:
                self.total = total
            if current:
                self.current = min(current, total)

        if not self.running:
            self.start()
