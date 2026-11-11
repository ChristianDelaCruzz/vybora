
import subprocess
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class PythonFileHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.last_restart = 0

    def start_app(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()

        self.process = subprocess.Popen([sys.executable, "main.py"])
        print("VyBora started!")

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            now = time.time()

            if now - self.last_restart > 1:
                self.last_restart = now
                print("Python file changed. Restarting VyBora...")
                self.start_app()


if __name__ == "__main__":
    handler = PythonFileHandler()
    observer = Observer()

    observer.schedule(handler, path=".", recursive=True)
    observer.start()

    handler.start_app()

    print("Watching Python files for changes...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

        if handler.process and handler.process.poll() is None:
            handler.process.terminate()

    observer.join()
