import asyncio
import adafruit_dht
import board

class DHT:
    def __init__(self):
        self.dht = adafruit_dht.DHT11(board.D5)
        self.temp = 0 # can this be set to null instead

    async def detect(self):
        try:
            while True:
                temp = self.dht.temperature

                if temp != self.temp:
                    self.temp = temp
                    return temp

                await asyncio.sleep(1)
        except asyncio.CancelledError:
            self.temp = 0

    def deinit(self):
        self.dht.exit()