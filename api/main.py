from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mqtt import FastMQTT, MQTTConfig

app = FastAPI()

# CORS origins
origins = [
    "*"
]

# midlertidig "database" :))
current_task = {
    1: 0,
    2: 0
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MQTT
mqtt_config = MQTTConfig(host = "mqtt20.iik.ntnu.no",
    port= 1883,
    keepalive = 60)
mqtt = FastMQTT(
    config=mqtt_config
)
mqtt.init_app(app)

# bryr vi oss om en respons her, eller skal vi bare sende alt over mqtt til dashboard hvis det blir requestet?
@app.get("/tasks")
def get_task():     
    return [
        {
            "group": 2,
            "task": {
                "id": 2,
                "title": "Create a sequence diagram",
            },
            "status": "Need help",
        },
        {
            "group": 8,
            "task": {
                "id": 9,
                "title": "Create a deployment diagram",
            },
            "status": "Need help",
        },
        {
            "group": 3,
            "task": {
                "id": 2,
                "title": "Create a sequence diagram",
            },
            "status": "Need help",
        }
    ]


@app.get("/tasks/{group_id}")
def get_task(group_id: int, next: bool, prev: bool): # samme funksjonsnavn som over??
    print(f"Get task for group {group_id}")
    if next and not prev:
        if current_task[group_id] < 9:
            current_task[group_id] += 1
        
    elif prev and not next:
        if current_task[group_id] > 0:
            current_task[group_id] -= 1


    mqtt.publish(f"rpi_ta_system/current_task/{group_id}", current_task[group_id])


@app.post("/help/{group_id}")
def ask_for_help(group_id: int) -> None:
    # Add group to a queue


    # Send notification to dashboard (publish)
    # https://pypi.org/project/fastapi-mqtt/
    mqtt.publish("rpi_ta_system/help_is_coming", f"{group_id}")

@app.get("/help_is_coming/{group_id}")
def help_is_coming(group_id: int) -> None:
    # Send notification to dashboard (publish)
    mqtt.publish("rpi_ta_system/help_is_coming", f"{group_id}")


@app.delete("/help/{group_id}")
def delete_help_request(group_id: int):
    # Remove group from queue
    # Inform dashboard
    pass


@app.patch("/tasks/{group_id}")
def update_task(group_id: int):
    # timestamp, task nr
    # Update data
    # Publish
    print(f"Update task for group {group_id}")
    return {
        "task": 1
    }