import asyncio

from picamera2 import Picamera2
from datetime import datetime
import cv2

class Camera:
    def __init__(self, location):
        self.cam = Picamera2()
        self.cam.start()
        self.location = location

    def save(self):
        image = self.cam.capture_array()
        cv2.imwrite(f"{self.location}/disarmed_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg", image)

    async def record(self):
        try:
            self.cam.start_recording(f"{self.location}/alert_{datetime.now().strftime("%Y%m%d_%H%M%S")}.mp4")
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            self.cam.stop_recording()

    def deinit(self):
        self.cam.close()