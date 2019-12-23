from watchdog.observers import Observer
import time
from watchdog.events import FileSystemEventHandler

import os
import json

USER_PATH = "/Users/orrgoren"
DSKTP_PATH = USER_PATH + "/desktop"
DCMNTS_PATH = USER_PATH + "/Documents"

class MyHandler(FileSystemEventHandler):
    i = 1
    def on_modified(self, event):
        for filename in os.listdir(folder_to_track):
            # get file extension
            src = folder_to_track + "/" + filename
            m = filename.split('.')
            ext = m[len(m) - 1].lower()
            if (ext == "png" or ext == "jpg" or ext == "jpeg"):
                newDest = DSKTP_PATH + "/images" + "/" + filename
            elif (ext  == "xlsx" or ext == "pdf" or ext == "docx"):
                newDest = DCMNTS_PATH + "/" + filename
            else:
                newDest = DSKTP_PATH + "/dontknow" + "/" + filename
            if not os.path.exists(newDest):
                os.makedirs(newDest)
            print("Moved: " + src + " | To: " + newDest)
            os.rename(src, newDest)

folder_to_track = DSKTP_PATH + "/sort"
event_handler = MyHandler()
observer = Observer()
observer.schedule(event_handler, folder_to_track, recursive=True)
observer.start()

try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    observer.stop()
observer.join()