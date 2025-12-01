import asyncio
import adafruit_dht
import board

class DHT:
    def __init__(self, pin, topic, retries=5):
        self.dht = adafruit_dht.DHT11(pin)
        self.retries = retries
        self.topic = topic

    async def detect(self, lastTemp):
            for attempt in range(self.retries):
                try:
                    temp = self.dht.temperature
                    if temp is not None and temp != lastTemp:
                        lastTemp = temp
                        return temp
                except RuntimeError:
                    await asyncio.sleep(0.5)
                await asyncio.sleep(0.1)
            return lastTemp

    def deinit(self):
        self.dht.exit()