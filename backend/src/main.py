import asyncio
from multiprocessing.managers import State

from dotenv import load_dotenv
import os
import board

from backend.src.controllers.Mailer_Controller import Mailer_Controller
from controllers.LEDS_Controller import LEDSController
from controllers.MQTT_Controller import MQTT_Controller
from backend.src.controllers.Logs_Controller import LOGS_Controller
from utils.Camera import Camera
from utils.Montion_Detector import Montion_Detector_Controller
from controllers.Screen_Controller import Screen_Controller
# from utils.Key_Scanner import Key_scanner
from utils.Button import Button
from utils.Buzzer import Buzzer
from utils.DHT import DHT
from utils.State import State

load_dotenv()

class AlarmSystem:
    def __init__(self):
        self.topics = os.getenv("TOPICS").split(",")
        self.led_blink_interval = float(os.getenv("LED_BLINK_INTERVAL"))
        self.detection_delay = int(os.getenv("DETECTION_DELAY"))
        self.alarm_delay = int(os.getenv("ALARM_DELAY"))
        self.logs = LOGS_Controller(os.getenv("LOGS_LOCATION"))
        self.mqtt = MQTT_Controller(os.getenv("MQTT_HOST"), int(os.getenv("MQTT_PORT")), int(os.getenv("MQTT_TIMEOUT")), os.getenv("MQTT_USERNAME"), os.getenv("MQTT_KEY"), self.logs)
        self.leds = LEDSController(self.led_blink_interval)
        self.screen = Screen_Controller()
        self.motion_detector = Montion_Detector_Controller()
        # self.key_scanner = Key_scanner()
        self.button = Button(board.D12)
        self.buzzer = Buzzer(board.D18)
        self.dht = DHT(board.D5, self.topics[1])
        self.camera = Camera(os.getenv("MEDIA_LOCATION"), os.getenv("IMAGE_LOCATION"), os.getenv("VIDEO_LOCATION"))
        self.mail = Mailer_Controller(os.getenv("SMTP_HOST"), os.getenv("SMTP_PORT"), os.getenv("SMTP_USER"), os.getenv("SMTP_PWD"), os.getenv("ALERT_FROM"), os.getenv("ALERT_TO"))

    async def main(self):
        try:
            while True:
                await self.idle()

                arming_system = await self.activate_alarm()

                if arming_system:
                    self.mqtt.save(self.topics[0], State.ARMED)
                    self.logs.save(self.topics[0], State.ARMED)
                    await self.motion_detector.detect()

                    disarming_system = await self.deactivate_alarm()

                    if not disarming_system:
                        await self.alert()
                    else:
                        self.camera.save()
        except asyncio.CancelledError:
            self.leds.deinit()
            self.motion_detector.deinit()
            self.button.deinit()
            self.buzzer.deinit()
            self.dht.deinit()
            self.camera.deinit()
            #self.screen.deinit()

    async def idle(self):
        self.mqtt.save(self.topics[0], State.DISARMED)
        self.logs.save(self.topics[0], State.DISARMED)

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
        lastTemp = float(self.logs.getLatest(self.dht.topic))
        while True:
            temp = await self.dht.detect(lastTemp)
            if temp != lastTemp:
                lastTemp = temp
                self.mqtt.save(self.dht.topic, temp)
                self.logs.save(self.dht.topic, temp)
                self.screen.temp(temp)

    async def activate_alarm(self):
        self.mqtt.save(self.topics[0], State.ARMING)
        self.logs.save(self.topics[0], State.ARMING)

        activate_task = asyncio.create_task(self.leds.start(self.alarm_delay))
        cancel_task = asyncio.create_task(self.button.onClick())
        buzzer_task = asyncio.create_task(self.buzzer.warning(self.led_blink_interval))
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
        self.mqtt.save(self.topics[0], State.DISARMING)
        self.logs.save(self.topics[0], State.DISARMING)

        # deactivate_task = asyncio.create_task(self.key_scanner.detect())
        deactivate_task = asyncio.create_task(self.button.onClick())
        light_task = asyncio.create_task(self.leds.warning())
        buzzer_task = asyncio.create_task(self.buzzer.warning(self.led_blink_interval))
        screen_task = asyncio.create_task(self.screen.delay(self.detection_delay))

        done, pending = await asyncio.wait(
            {deactivate_task, light_task, buzzer_task, screen_task},
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
        self.mqtt.save(self.topics[0], State.ALERT)
        self.logs.save(self.topics[0], State.ALERT)

        # deactivate_task = asyncio.create_task(self.key_scanner.detect())
        deactivate_task = asyncio.create_task(self.button.onClick())
        record_task = asyncio.create_task(self.camera.record())
        light_task = asyncio.create_task(self.leds.alert())
        buzzer_task = asyncio.create_task(self.buzzer.alert())
        self.screen.alert()
        self.mail.send_emergency_alert()

        done, pending = await asyncio.wait(
            {deactivate_task, record_task, light_task, buzzer_task},
            return_when = asyncio.FIRST_COMPLETED
        )

        for task in pending:
            task.cancel()

if __name__ == '__main__':
    alarm = AlarmSystem()
    asyncio.run(alarm.main())