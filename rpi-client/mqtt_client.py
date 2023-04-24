from threading import Thread

import paho.mqtt.client as mqtt
PREFIX = "rpi_ta_system"

class MQTT_Client:
    def __init__(self, stm_driver, group_id, rpi_logic):
        self.group_id = group_id
        self.stm_driver = stm_driver
        self.client = mqtt.Client()
        self.rpi_logic = rpi_logic
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print("on_connect(): {}".format(mqtt.connack_string(rc)))

    def on_message(self, client, userdata, msg):
        print("on_message(): topic: {}".format(msg.topic))
        global PREFIX
        if msg.topic == f"{PREFIX}/help_is_coming":
            print(f"Payload: {msg.payload}")
            if int(msg.payload) == self.group_id:
                self.stm_driver.send("help_is_coming", "rpi")
        elif msg.topic == f"{PREFIX}/current_task/{self.group_id}":
            self.rpi_logic.task = int(msg.payload)
            self.stm_driver.send("task_arrival", "rpi")
        elif msg.topic == f"{PREFIX}/help_finished":
            print(f"HELP FINISHED: {self.group_id}")
            if int(msg.payload) == self.group_id:
                self.stm_driver.send("help_finished", "rpi")


    def start(self, broker, port):

        print("Connecting to {}:{}".format(broker, port))
        self.client.connect(broker, port)

        self.client.subscribe(f"{PREFIX}/help_is_coming")
        self.client.subscribe(f"{PREFIX}/current_task/{self.group_id}")
        self.client.subscribe(f"{PREFIX}/help_finished")

        try:
            # line below should not have the () after the function!
            thread = Thread(target=self.client.loop_forever)
            thread.start()
        except KeyboardInterrupt:
            print("Interrupted")
            self.client.disconnect()