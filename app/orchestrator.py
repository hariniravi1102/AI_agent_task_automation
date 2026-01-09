import yaml
from pathlib import Path
from datetime import datetime

from agents import AGENT_REGISTRY
from db.session import SessionLocal
from db.models import Job, Step




WORKFLOW_DIR = Path("workflows")


def select_workflow(event):

    for wf_file in WORKFLOW_DIR.glob("*.yaml"):
        with open(wf_file, "r") as f:
            workflow = yaml.safe_load(f)["workflow"]

            if workflow["trigger"]["event_type"] == event.event_type:
                return workflow

    return None




def execute_workflow(workflow: dict, event):

    db = SessionLocal()


    job = Job(
        event_type=event.event_type,
        source=event.source,
        status="RUNNING"
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    print(f"\n Executing workflow: {workflow['name']}", flush=True)


    payload = event.payload.copy()
    payload["job_id"] = str(job.id)
    payload["event_type"] = event.event_type
    payload["source"] = event.source
    payload["trigger_type"] = event.event_type

    execution_log = []

    try:

        for step_cfg in workflow["steps"]:
            step = Step(
                job_id=job.id,
                step_name=step_cfg["id"],
                agent=step_cfg["agent"],
                status="RUNNING",
                attempts=0
            )
            db.add(step)
            db.commit()
            db.refresh(step)

            max_retries = step_cfg.get("retry", 0)
            on_failure = step_cfg.get("on_failure", "STOP")

            agent = AGENT_REGISTRY.get(step_cfg["agent"])
            if not agent:
                raise RuntimeError(f"Agent not registered: {step_cfg['agent']}")

            print(
                f" START step: {step.step_name} "
                f"(agent={step.agent}, max_retries={max_retries})",
                flush=True
            )

            success = False


            while step.attempts <= max_retries:
                step.attempts += 1
                db.commit()


                result = agent.run(payload)

                if result.success:
                    step.status = "SUCCESS"
                    db.commit()

                    print(
                        f"COMPLETE step: {step.step_name} "
                        f"(attempts={step.attempts})",
                        flush=True
                    )

                    execution_log.append({
                        "step": step.step_name,
                        "status": "SUCCESS",
                        "attempts": step.attempts
                    })

                    success = True
                    break

                else:
                    step.error = result.error
                    db.commit()

                    print(
                        f" FAILED attempt {step.attempts} "
                        f"for step: {step.step_name} → {result.error}",
                        flush=True
                    )

                    if step.attempts > max_retries:
                        break


            if not success:
                step.status = "FAILED"
                db.commit()

                execution_log.append({
                    "step": step.step_name,
                    "status": "FAILED",
                    "attempts": step.attempts,
                    "error": step.error
                })

                print(
                    f" STEP FAILED: {step.step_name} "
                    f"(policy={on_failure})",
                    flush=True
                )

                if on_failure == "STOP":
                    job.status = "FAILED"
                    db.commit()
                    print(" WORKFLOW STOPPED", flush=True)
                    return execution_log

                elif on_failure == "CONTINUE":
                    print("CONTINUING TO NEXT STEP", flush=True)
                    continue


        job.status = "SUCCESS"
        job.completed_at = datetime.utcnow()
        db.commit()

        print(" Workflow completed successfully", flush=True)

    finally:
        db.close()

    return execution_log
