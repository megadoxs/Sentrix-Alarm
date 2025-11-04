import digitalio

class LED:
    def __init__(self, pin):
        self.pin = digitalio.DigitalInOut(pin)
        self.pin.direction = digitalio.Direction.OUTPUT
        self.pin.value = False

    def on(self):
        self.pin.value = True

    def off(self):
        self.pin.value = False

    def toggle(self):
        self.pin.value = not self.pin.value

    def deinit(self):
        self.pin.deinit()