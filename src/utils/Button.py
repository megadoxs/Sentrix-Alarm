import digitalio
import asyncio

class Button:
    def __init__(self, pin):
        self.pin = digitalio.DigitalInOut(pin)
        self.pin.direction = digitalio.Direction.INPUT
        self.pin.pull = digitalio.Pull.UP

    async def onClick(self):
        while self.pin.value:
            await asyncio.sleep(0.05)

        while not self.pin.value:
            await asyncio.sleep(0.05)

    def deinit(self):
        self.pin.deinit()