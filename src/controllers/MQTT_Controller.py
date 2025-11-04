import paho.mqtt.client as mqtt
import csv
import os
from datetime import datetime

class MQTT_Controller:
    def __init__(self, broker, port, timeout, topics, username, key):
        try:
            self.topics = topics
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.username_pw_set(username, key)
            self.mqtt_client.connect(broker, port, timeout)
            self.mqtt_client.loop_start()
            self.connected = True
            self.username = username

            for topic in self.topics:
                filename = f"{topic}.csv"
                if not os.path.exists(filename):
                    with open(filename, mode="w", newline="") as file:
                        writer = csv.writer(file)
                        writer.writerow(["timestamp", "message"])
        except Exception as e:
            self.connected = False

    # impl retry
    def _publish(self, topic, message):
        if not self.connected:
            return False

        try:
            result, _ = self.mqtt_client.publish(f"{self.username}/feeds/{topic}", str(message))
            return result == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            return False

    def _save(self, filename, message):
        filename = f"{filename}.csv"
        with open(filename, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([datetime.now().isoformat(), message])

    def status(self, status):
        topic = self.topics[0]
        self._save(topic, status)
        self._publish(topic, status)

    def temp(self, temp):
        topic = self.topics[1]
        self._save(topic, temp)
        self._publish(topic, temp)
