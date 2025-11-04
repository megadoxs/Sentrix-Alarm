import asyncio
from datetime import datetime

import board
import digitalio
import adafruit_character_lcd.character_lcd as character_lcd

class Screen_Controller:
    def __init__(self):
        lcd_rs = digitalio.DigitalInOut(board.D23)
        lcd_en = digitalio.DigitalInOut(board.D24)
        lcd_d4 = digitalio.DigitalInOut(board.D6)
        lcd_d5 = digitalio.DigitalInOut(board.D13)
        lcd_d6 = digitalio.DigitalInOut(board.D19)
        lcd_d7 = digitalio.DigitalInOut(board.D26)
        lcd_columns = 16
        lcd_rows = 2
        self.lcd = character_lcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows)
        self.line1 = ""
        self.line2 = ""

    async def delay(self, delay):
        try:
            for i in range(delay):
                self.lcd.clear()
                self.lcd.message = f"Delay: {delay - i}s"
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            self.lcd.clear()

    def _update_display(self):
        self.lcd.clear()
        self.lcd.message = f"{self.line1}\n{self.line2}"

    async def time(self):
        try:
            while True:
                now = datetime.now().strftime("%H:%M:%S")
                self.line1 = f"Time: {now}"
                self._update_display()
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            self.lcd.clear()

    def temp(self, temp):
        self.line2 = f"Temp: {temp}\xDFC"
        self._update_display()

#    def deinit(self):
#        self.lcd.deinit()