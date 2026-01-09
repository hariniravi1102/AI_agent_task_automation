from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time

from app.event_model import Event
from app.orchestrator import select_workflow, execute_workflow

def scheduled_document_job():


    print("\n  Scheduled job triggered", flush=True)

    event = Event(
        event_type="DOCUMENT_RECEIVED",
        source="scheduler",
        payload={
            "filename": "scheduled_dummy.csv",
            "path": "N/A",
            "file_type": "csv",
            "triggered_at": datetime.utcnow().isoformat()
        }
    )

    workflow = select_workflow(event)

    if not workflow:
        print(" No workflow found for scheduled event", flush=True)
        return

    execute_workflow(workflow, event)



def start_scheduler():
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        scheduled_document_job,
        trigger="interval",
        seconds=30,
        id="document_scheduler"
    )

    scheduler.start()
    print(" Scheduler started (runs every 30 seconds)", flush=True)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()


if __name__ == "__main__":
    start_scheduler()
