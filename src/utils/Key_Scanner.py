import asyncio
from mfrc522 import SimpleMFRC522



class Key_scanner:
    def __init__ (self):
        self.scanner = SimpleMFRC522()

    async def detect(self):
        return self.scanner.read()