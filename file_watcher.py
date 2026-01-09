import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.orchestrator import select_workflow, execute_workflow
from app.event_model import Event
from pathlib import Path


WATCH_DIR = Path("watch/incoming")

class CSVHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        if file_path.suffix.lower() != ".csv":
            return

        print(f"\n New CSV detected: {file_path.name}")

        event_data = Event(
            event_type="DOCUMENT_RECEIVED",
            source="file",
            payload={
                "filename": file_path.name,
                "path": str(file_path),
                "file_type": "csv"
            }
        )

        print("Selecting workflow...")
        workflow = select_workflow(event_data)

        if not workflow:
            print(" NO WORKFLOW FOUND for event:", event_data.event_type)
            return

        print("Workflow selected:", workflow["name"])
        print("Calling execute_workflow()")

        execute_workflow(workflow, event_data)


def start_file_watcher():
    WATCH_DIR.mkdir(parents=True, exist_ok=True)

    observer = Observer()
    handler = CSVHandler()
    observer.schedule(handler, str(WATCH_DIR), recursive=False)

    observer.start()
    print(f"Watching folder: {WATCH_DIR.resolve()}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    start_file_watcher()
