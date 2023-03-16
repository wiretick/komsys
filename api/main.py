from fastapi import FastAPI

app = FastAPI()


@app.get("/dashboard/{subject}")
def dashboard():
    return "Dashboard website files..."


@app.get("/task/{group_id}")
def get_task(group_id: int):
    print(f"Get task for group {group_id}")
    return {
        "task": 1
    }

@app.post("/help/{group_id}")
def ask_for_help(group_id: int):
    # Add group to a queue
    # Send notification to dashboard (publish)
    pass

@app.delete("/help/{group_id}")
def delete_help_request(group_id: int):
    # Remove group from queue
    # Inform dashboard
    pass

@app.patch("/task/{group_id}")
def update_task(group_id: int):
    # timestamp, task nr
    # Update data
    # Publish
    print(f"Update task for group {group_id}")
    return {
        "task": 1
    }