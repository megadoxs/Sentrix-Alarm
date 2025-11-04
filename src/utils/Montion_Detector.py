
import digitalio
import board
import asyncio

class Montion_Detector_Controller:
    def __init__(self):
        self.pir = digitalio.DigitalInOut(board.D4)
        self.pir.direction = digitalio.Direction.INPUT
        self.pir.pull = digitalio.Pull.DOWN

    async def detect(self):
        while True:
            if self.pir.value:
                break
            await asyncio.sleep(0.5)

    def deinit(self):
        self.pir.deinit()