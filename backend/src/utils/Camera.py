import asyncio

from picamera2 import Picamera2
from datetime import datetime
from picamera2.encoders import H264Encoder
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

class Camera:
    def __init__(self, media, img, vid):
        self.cam = Picamera2()
        self.cam.start()
        self.image = os.path.join(BASE_DIR, media, img)
        self.video = os.path.join(BASE_DIR, media, vid)

        os.makedirs(self.image, exist_ok=True)
        os.makedirs(self.video, exist_ok=True)

    def save(self):
        self.cam.start_and_capture_file(os.path.join(str(self.image), f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"))

    async def record(self):
        try:
            self.cam.start_recording(H264Encoder(), os.path.join(str(self.video), f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.h264"))
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            self.cam.stop_recording()

    def deinit(self):
        self.cam.close()