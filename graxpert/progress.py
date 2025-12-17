from queue import Empty, Queue
from threading import Thread

class DynamicProgressThread(Thread):
    def __init__(self, interval=1, total=100, callback=None):
        Thread.__init__(self)
        self.daemon = True
        self.interval = interval
        self.callback = callback
        self.total = total
        self.current_progress = 0
        self.update_queue = Queue()
        self.start()

    def run(self):
        while True:
            try:
                # display every interval secs
                task = self.update_queue.get(timeout=self.interval)
            except Empty:
                continue

            current_progress, total = task
            self.update_queue.task_done()
            if current_progress == total:
                # once we have done uploading everything return
                self.done_progress()
                return

    # minio needs this method
    def set_meta(self, total_length, object_name=None):
        self.total = total_length

    def update(self, size):
        if not isinstance(size, int):
            raise ValueError(f"{type(size)} type can not be displayed. Please change it to Int.")

        self.current_progress += size
        self.update_queue.put((self.current_progress, self.total))

        if self.callback is not None:
            self.callback(self.progress())

    def done_progress(self):
        self.total = 0
        self.current_progress = 0

    def progress(self):
        if self.total == 0:
            return 0
        return float(self.current_progress) / float(self.total)
