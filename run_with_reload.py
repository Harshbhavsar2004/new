import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import os
import shutil

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, target_folder, raw_folder):
        self.target_folder = target_folder
        self.raw_folder = raw_folder

    def on_created(self, event):
        if not event.is_directory:
            print(f"New file detected: {event.src_path}")
            self.copy_to_target_folder(event.src_path)

    def copy_to_target_folder(self, file_path):
        try:
            file_name = os.path.basename(file_path)
            target_path = os.path.join(self.target_folder, file_name)
            shutil.copy2(file_path, target_path)
            print(f"Copied {file_name} to Target Folder.")
            restart_program()
        except Exception as e:
            print(f"Failed to copy {file_path}: {str(e)}")

def restart_program():
    python = sys.executable
    subprocess.call([python, "main.py"])

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    raw_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Raw Folder")
    target_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Target Folder")
    os.makedirs(raw_folder, exist_ok=True)
    os.makedirs(target_folder, exist_ok=True)

    event_handler = ChangeHandler(target_folder, raw_folder)
    observer = Observer()
    observer.schedule(event_handler, raw_folder, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()