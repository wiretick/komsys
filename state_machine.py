from stmpy import Driver, Machine
import asyncio
from evdev import InputDevice
from sense_hat import SenseHat
from mqtt_client import MQTT_Client

import requests

URL = "http://localhost:8000"
GROUP_ID = 1
broker, port = "mqtt20.iik.ntnu.no", 1883
CURRENT_TASK = 0

class RpiLogic():

    def __init__(self):
        self.hat = SenseHat()

    def initial(self):
        print("STATE: initial")
        global CURRENT_TASK
        self.task = CURRENT_TASK
        # self.hat.show_message("komsys")

    def display_current_task(self):
        print(f"STATE: display_current_task: {self.task}")
        self.hat.show_letter(str(self.task))

    def get_next_task(self):
        print("get_next_task")

    def get_prev_task(self):
        print("get_prev_task")

    def display_help(self):
        print("display_waiting_for_help")
        for i in range(8):
            for j in range(8):
                self.hat.set_pixel(i,j, (255,0,0))

    def display_waiting(self):
        print("display_waiting")
        self.hat.show_letter("X")

    def send_help_request(self):
        print("send_help_request")
        # r = requests.post(f"{URL}/help/{GROUP_ID}", json={"task": self.task})
    
    def help_finished(self):
        print("help_finished")
        # r = requests.delete(f"{URL}/help/{GROUP_ID}")

working_on_task = {'name': 'working_on_task',
                   'entry': 'display_current_task'}

waiting_for_help = {'name': 'waiting_for_help',
                    'entry': 'send_help_request',
                    'entry': 'display_help',
                    'exit': 'help_finished'}

waiting_for_task_number = {'name': "waiting_for_task_number",
                           'entry': "display_waiting"}

states = [working_on_task, waiting_for_help, waiting_for_task_number]

t0 = {'source': 'initial', 'target': 'working_on_task', 'effect': 'initial'}

enter_help = {'trigger': 'help_button',
             'source': 'working_on_task',
             'target': 'waiting_for_help'}

exit_help = {'trigger': 'help_button',
             'source': 'waiting_for_help', 
             'target': 'working_on_task'}

exit_help_mqtt = {'trigger': 'help_is_coming',
                  'source': 'waiting_for_help',
                  'target': 'working_on_task'}

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


transitions = [t0, enter_help, exit_help, next_task, prev_task, task_arrival, exit_help_mqtt]

driver = Driver()
rpilogic = RpiLogic()
machine = Machine(name='rpi', transitions=transitions, states=states,obj=rpilogic)
rpilogic.stm = machine
driver.add_machine(machine)
driver.start()
mq_client = MQTT_Client(driver, GROUP_ID, rpilogic)
mq_client.start(broker, port)

dev = InputDevice('/dev/input/event3')

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