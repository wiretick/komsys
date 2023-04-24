from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mqtt import FastMQTT, MQTTConfig
from sse_starlette.sse import EventSourceResponse
import asyncio
from enum import Enum

app = FastAPI()

# CORS origins
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MQTT
mqtt_config = MQTTConfig(
    host = "mqtt20.iik.ntnu.no",
    port = 1883,
    keepalive = 60
)
mqtt = FastMQTT(
    config=mqtt_config
)
mqtt.init_app(app)


class Status(Enum):
    WAITING = 'Waiting'
    GETTING_HELP = 'Getting help'
    WORKING = 'Working'

groups = [
    {
        "group": 1,
        "task": 1,
        "status": Status.WORKING
    },
    {
        "group": 2,
        "task": 1,
        "status": Status.WORKING
    },
    {
        "group": 3,
        "task": 1,
        "status": Status.WAITING
    }
]

help_queue = [3]

def queue():
    return [g for g in groups if g['group'] in help_queue]


# bryr vi oss om en respons her, eller skal vi bare sende alt over mqtt til dashboard hvis det blir requestet?
@app.get("/tasks")
def get_tasks():
    return groups


@app.get("/queue")
def get_queue():
    # TODO fix ordering, not getting ordered according to help_queue, but by groups list.
    return queue()


@app.get("/tasks/{group_id}")
def get_task(group_id: int, next: bool, prev: bool): # samme funksjonsnavn som over??
    print(f"Get task for group {group_id}")

    if next and not prev:
        if groups[group_id-1]["task"] < 9:
            groups[group_id-1]["task"] += 1
        
    elif prev and not next:
        if groups[group_id-1]["task"] > 0:
            groups[group_id-1]["task"] -= 1


    mqtt.publish(f"rpi_ta_system/current_task/{group_id}", groups[group_id-1]["task"])


@app.post("/help/{group_id}")
def ask_for_help(group_id: int) -> None:
    # Add group to a queue
    # Send notification to dashboard (publish)
    # https://pypi.org/project/fastapi-mqtt/
    groups[group_id-1]["status"] = Status.WAITING
    help_queue.append(group_id)
    mqtt.publish("rpi_ta_system/help_is_coming", f"{group_id}")


@app.post("/help_is_coming/{group_id}")
def help_is_coming(group_id: int) -> None:
    groups[group_id-1]["status"] = Status.GETTING_HELP
    mqtt.publish("rpi_ta_system/help_is_coming", f"{group_id}")


@app.delete("/help/{group_id}")
def delete_help_request(group_id: int):
    # Remove group from queue
    help_queue.pop(help_queue.index(group_id))
    groups[group_id-1]["status"] = Status.WORKING

    # Publish?


@app.patch("/group/{group_id}/tasks/{task_nr}")
def update_task(group_id: int, task_nr: int):
    # Publish
    groups[group_id-1]["task"] = task_nr

    return {
        "group": group_id,
        "task": task_nr
    }


# Notfications for frontend
notifications = []

@mqtt.subscribe("rpi_ta_system/help_is_needed")
async def message_to_topic(client, topic, payload, qos, properties):
    # print("Received message to specific topic: ", topic, qos, properties)
    group_nr = int(payload.decode())
    groups[group_nr-1]["status"] = Status.WAITING
    help_queue.append(group_nr)
    notifications.append(f"Group number {group_nr} just requested help!")

async def new_notification():
    while True:
        for i,n in enumerate(notifications):
            yield n
            notifications.pop(i)

        await asyncio.sleep(2)

@app.get('/notifications')
async def get_notifications(request: Request): 
    generator = new_notification()
    return EventSourceResponse(generator)