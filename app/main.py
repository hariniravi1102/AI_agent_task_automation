from fastapi import FastAPI
from app.event_model import Event
from app.orchestrator import select_workflow, execute_workflow
from admin.routes import router as admin_router

from fastapi.staticfiles import StaticFiles



app = FastAPI(title="Task Automation Platform")
app.include_router(admin_router)
app.mount(
    "/static",
    StaticFiles(directory="admin/static"),
    name="static"
)

@app.post("/event")
def receive_event(event: Event):
    workflow = select_workflow(event)

    if not workflow:
        return {
            "status": "NO_WORKFLOW_FOUND",
            "event_type": event.event_type
        }

    execution_log = execute_workflow(workflow, event)

    return {
        "status": "WORKFLOW_EXECUTED",
        "workflow_name": workflow["name"],
        "execution": execution_log
    }
