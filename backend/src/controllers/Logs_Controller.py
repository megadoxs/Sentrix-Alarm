import csv
import os
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

class LOGS_Controller:
    def __init__(self, dir):
        try:
            self.dir = os.path.join(BASE_DIR, dir)
            os.makedirs(self.dir, exist_ok=True)
        except Exception as e:
            self.connected = False

    def save(self, file, message):
        filename = self._getFile(file)
        file_exists = os.path.exists(filename)

        with open(filename, mode="a", newline="") as file:
            writer = csv.writer(file)

            if not file_exists:
                writer.writerow(["timestamp", "message"])

            writer.writerow([datetime.now().strftime('%H:%M:%S'), message])

    def getLatest(self, file):
        filename = self._getFile(file)

        if not os.path.exists(filename):
            return None

        with open(filename, "rb") as f:
            f.seek(0, os.SEEK_END)
            pos = f.tell()

            while pos > 0:
                pos -= 1
                f.seek(pos)
                if f.read(1) == b'\n':
                    break

            last_line = f.readline().decode().strip()

            if not last_line:
                return None

            row = next(csv.reader([last_line]))
            return row[1] if len(row) > 1 else None

    def _getFile(self, file):
        return os.path.join(str(self.dir), f"{datetime.now().strftime("%Y-%m-%d")}_{file}.csv")