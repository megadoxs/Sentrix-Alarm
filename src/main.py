import asyncio
from multiprocessing.managers import State

from dotenv import load_dotenv
import os
import board
from controllers.LEDS_Controller import LEDSController
from controllers.MQTT_Controller import MQTT_Controller
from utils.Camera import Camera
from utils.Montion_Detector import Montion_Detector_Controller
from controllers.Screen_Controller import Screen_Controller
from utils.Key_Scanner import Key_scanner
from utils.Button import Button
from utils.Buzzer import Buzzer
from utils.DHT import DHT
from utils.State import State

load_dotenv()

class AlarmSystem:
    def __init__(self):
        self.led_blink_interval = float(os.getenv("LED_BLINK_INTERVAL"))
        self.detection_delay = int(os.getenv("DETECTION_DELAY"))
        self.alarm_delay = int(os.getenv("ALARM_DELAY"))
        self.mqtt = MQTT_Controller(os.getenv("MQTT_HOST"), int(os.getenv("MQTT_PORT")), int(os.getenv("MQTT_TIMEOUT")), os.getenv("TOPICS").split(","), os.getenv("MQTT_USERNAME"), os.getenv("MQTT_KEY"))
        self.leds = LEDSController(self.led_blink_interval)
        self.screen = Screen_Controller()
        self.motion_detector = Montion_Detector_Controller()
        self.key_scanner = Key_scanner()
        self.button = Button(board.D12)
        self.buzzer = Buzzer(board.D18)
        self.dht = DHT()
        self.camera = Camera(os.getenv("IMAGE_LOCATION"))

    async def main(self):
        try:
            while True:
                self.mqtt.status(State.DISARMED)
                await self.idle()

                self.mqtt.status(State.ARMING)
                arming_system = await self.activate_alarm()

                if arming_system:
                    self.mqtt.status(State.ARMED)
                    await self.motion_detector.detect()

                    self.mqtt.status(State.DISARMING)
                    disarming_system = await self.deactivate_alarm()

                    if not disarming_system:
                        self.camera.save()
                        self.mqtt.status(State.ALERT)
                        await self.alert()
        except asyncio.CancelledError:
            self.leds.deinit()
            self.motion_detector.deinit()
            self.button.deinit()
            self.buzzer.deinit()
            self.dht.deinit()
            self.camera.deinit()
            #self.screen.deinit()

    async def idle(self): 
        activate_task = asyncio.create_task(self.button.onClick())
        time_task = asyncio.create_task(self.screen.time())
        temp_task = asyncio.create_task(self.temp())

        done, pending = await asyncio.wait(
            {activate_task, time_task, temp_task},
            return_when = asyncio.FIRST_COMPLETED
        )

        for task in pending:
            task.cancel()

    async def temp(self):
        while True:
            temp = await self.dht.detect()
            self.mqtt.temp(temp)
            self.screen.temp(temp)

    async def activate_alarm(self):
        activate_task = asyncio.create_task(self.leds.start(self.alarm_delay))
        cancel_task = asyncio.create_task(self.button.onClick())
        buzzer_task = asyncio.create_task(self.buzzer.warning())
        screen_task = asyncio.create_task(self.screen.delay(self.alarm_delay))

        done, pending = await asyncio.wait(
            {activate_task, cancel_task, buzzer_task, screen_task},
            return_when = asyncio.FIRST_COMPLETED
        )

        for task in pending:
            task.cancel()

        finished_task = done.pop()

        if finished_task == activate_task:
            return True
        return False

    async def deactivate_alarm(self):
        deactivate_task = asyncio.create_task(self.key_scanner.detect())
        light_task = asyncio.create_task(self.leds.warning())
        buzzer_task = asyncio.create_task(self.buzzer.warning())
        screen_task = asyncio.create_task(self.screen.delay(self.detection_delay))

        done, pending = await asyncio.wait(
            {deactivate_task, light_task, buzzer_task, screen_task},
            timeout = self.detection_delay,
            return_when = asyncio.FIRST_COMPLETED
        )

        for task in pending:
            task.cancel()

        if not done:
            return False

        finished_task = done.pop()
        if finished_task == deactivate_task:
            return True
        return False

    async def alert(self):
        deactivate_task = asyncio.create_task(self.key_scanner.detect())
        record_task = asyncio.create_task(self.camera.record())
        light_task = asyncio.create_task(self.leds.alert())
        self.buzzer.on()

        done, pending = await asyncio.wait(
            {deactivate_task, record_task, light_task},
            return_when = asyncio.FIRST_COMPLETED
        )

        for task in pending:
            task.cancel()

        self.buzzer.off()

if __name__ == '__main__':
    alarm = AlarmSystem()
    asyncio.run(alarm.main())