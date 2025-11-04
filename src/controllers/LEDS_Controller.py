

import utils.LED
from utils.LED import LED
import board
import time
import asyncio


class LEDSController:
    def __init__(self, interval):
        self.interval = interval
        self.leds = [
            LED(board.D16), # Green LED
            LED(board.D20), # Yellow LED
            LED(board.D21)  # Red LED
        ]
        self.leds[0].on() # Enables the green LED by default

    async def start(self, delay): # used to arm system
        try:
            self.leds[0].off()  # turns green LED off

            start_time = time.time()
            while time.time() - start_time < delay: # blinks yellow LED
                self.leds[1].toggle()
                await asyncio.sleep(self.interval) # blink time

            self.leds[1].off()  # turns yellow LED off
            self.leds[2].on()   # turns red LED on
        except asyncio.CancelledError:
            self.leds[0].on()
            self.leds[1].off()


    def reset(self):
        self.leds[2].off() # turns red LED off
        self.leds[0].on()  # turns green LED on

    async def warning(self): # used in disarm
        try:
            self.leds[2].off()

            while True:
                self.leds[1].toggle()
                await asyncio.sleep(self.interval)
        except asyncio.CancelledError:
            self.leds[1].off()
            self.leds[0].on()

    async def alert(self):
        try:
            while True:
                self.leds[2].toggle()
                await asyncio.sleep(self.interval)
        except asyncio.CancelledError:
            self.leds[2].off()

    
    def deinit(self):
        for led in self.leds:
            led.deinit()