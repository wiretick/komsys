from stmpy import Driver, Machine
import asyncio
import evdev
from sense_hat import SenseHat
from mqtt_client import MQTT_Client
from json import dumps

URL = "http://slim7.local:8000"
GROUP_ID = 1
broker, port = "mqtt20.iik.ntnu.no", 1883
CURRENT_TASK = 0
PREFIX = "rpi_ta_system"

class RpiLogic():

    def __init__(self):
        self.hat = SenseHat()

    def initial(self):
        print("STATE: initial")
        global CURRENT_TASK
        self.task = CURRENT_TASK
        self.mq_client.client.publish(f"{PREFIX}/get_current_task/{GROUP_ID}", dumps({"next": False, "prev": False}), qos=2)

    def display_current_task(self):
        print(f"STATE: display_current_task: {self.task}")
        self.hat.show_letter(str(self.task))

    def get_next_task(self):
        print("get_next_task")
        self.mq_client.client.publish(f"{PREFIX}/get_current_task/{GROUP_ID}", dumps({"next": True, "prev": False}), qos=2)

    def get_prev_task(self):
        print("get_prev_task")
        self.mq_client.client.publish(f"{PREFIX}/get_current_task/{GROUP_ID}", dumps({"next": False, "prev": True}), qos=2)

    def display_red(self):
        print("display_waiting_for_help")
        for i in range(8):
            for j in range(8):
                self.hat.set_pixel(i,j, (255,0,0))

    def display_green(self):
        for i in range(8):
            for j in range(8):
                self.hat.set_pixel(i,j, (0,255,0))


    def display_waiting(self):
        print("display_waiting")
        self.hat.show_letter("X")

    def send_help_request(self):
        self.display_red()
        print("send_help_request")
        self.mq_client.client.publish(f"{PREFIX}/ask_for_help/{GROUP_ID}", "" , qos=2)

    def help_no_longer_needed(self):
        print("help_no_longer_needed")
        self.mq_client.client.publish(f"{PREFIX}/delete_help_request/{GROUP_ID}", "" , qos=2)

working_on_task = {'name': 'working_on_task',
                   'entry': 'display_current_task'}

waiting_for_help = {'name': 'waiting_for_help',
                    'entry': 'send_help_request'
                    }

waiting_for_task_number = {'name': "waiting_for_task_number",
                           'entry': "display_waiting"}

help_in_progress = {'name': 'help_in_progress',
                          'entry': 'display_green'}

states = [working_on_task, waiting_for_help, waiting_for_task_number, help_in_progress]

t0 = {'source': 'initial', 'target': 'working_on_task', 'effect': 'initial'}

enter_help = {'trigger': 'help_button',
             'source': 'working_on_task',
             'target': 'waiting_for_help'}

task_arrival_loop = {'trigger': 'task_arrival',
                     'source': 'working_on_task',
                     'target': 'working_on_task'}

help_finished_transition = {'trigger': 'help_finished',
                      'source': 'help_in_progress',
                      'target': 'working_on_task'}

exit_help = {'trigger': 'help_button',
             'source': 'waiting_for_help',
             'target': 'working_on_task',
             'effect': 'help_no_longer_needed'}

exit_help_mqtt = {'trigger': 'help_is_coming',
                  'source': 'waiting_for_help',
                  'target': 'help_in_progress'}

next_task = {'trigger': 'next_button',
             'source': 'working_on_task',
             'target': 'waiting_for_task_number',
             'effect': 'get_next_task'}

prev_task = {'trigger': 'prev_button',
             'source': 'working_on_task',
             'target': 'waiting_for_task_number',
             'effect': 'get_prev_task'}

task_arrival = {'trigger': 'task_arrival',
                'source': 'waiting_for_task_number',
                'target': 'working_on_task'}


transitions = [t0, enter_help, exit_help, next_task, prev_task,
                task_arrival, exit_help_mqtt, task_arrival_loop,
                help_finished_transition]

driver = Driver()
rpilogic = RpiLogic()
mq_client = MQTT_Client(driver, GROUP_ID, rpilogic)
rpilogic.mq_client = mq_client
machine = Machine(name='rpi', transitions=transitions, states=states,obj=rpilogic)
rpilogic.stm = machine
driver.add_machine(machine)
mq_client.start(broker, port)
driver.start()


def get_joystick():
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        if device.name == "Raspberry Pi Sense HAT Joystick":
            return device

dev = get_joystick()

# helper function to read the relevant events from the device
async def helper(dev):
    async for ev in dev.async_read_loop():
        if ev.value == 1 and ev.type == 1:
            if ev.code == 106:
                machine.send("next_button")
            elif ev.code == 105:
                machine.send("prev_button")
            elif ev.code == 28:
                machine.send("help_button")

loop = asyncio.get_event_loop()
loop.run_until_complete(helper(dev))