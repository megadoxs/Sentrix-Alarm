import digitalio
import asyncio

class Buzzer:
    def __init__(self, pin):
        self.pin = digitalio.DigitalInOut(pin)
        self.pin.direction = digitalio.Direction.OUTPUT
        self.pin.value = False

    def on(self):
        self.pin.value = True

    def off(self):
        self.pin.value = False

    async def warning(self):
        try:
            while True:
                self.on()
                await asyncio.sleep(1)
                self.off()
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            self.off()

    def deinit(self):
        self.pin.deinit()