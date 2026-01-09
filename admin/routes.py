from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, cast, Date
from pathlib import Path

from db.session import SessionLocal
from db.models import Job, Step, LLMDecision



router = APIRouter(prefix="/admin", tags=["admin"])

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "admin" / "templates")

print("TEMPLATES SEARCH PATH =", templates.env.loader.searchpath)
print(" admin.routes loaded")



@router.get("/", response_class=HTMLResponse)
def jobs_view(request: Request):
    db = SessionLocal()
    jobs = db.query(Job).order_by(Job.created_at.desc()).all()
    db.close()

    return templates.TemplateResponse(
        "jobs.html",
        {"request": request, "jobs": jobs}
    )



@router.get("/job/{job_id}", response_class=HTMLResponse)
def job_detail(request: Request, job_id: str):
    db = SessionLocal()

    job = db.query(Job).get(job_id)
    steps = db.query(Step).filter(Step.job_id == job_id).all()
    decisions = db.query(LLMDecision).filter(
        LLMDecision.job_id == job_id
    ).all()

    db.close()

    return templates.TemplateResponse(
        "job_detail.html",
        {
            "request": request,
            "job": job,
            "steps": steps,
            "decisions": decisions
        }
    )



@router.get("/llm", response_class=HTMLResponse)
def llm_decision_list(request: Request):
    db = SessionLocal()

    decisions = (
        db.query(LLMDecision)
        .order_by(LLMDecision.created_at.desc())
        .all()
    )

    db.close()

    return templates.TemplateResponse(
        "llm_list.html",
        {
            "request": request,
            "decisions": decisions
        }
    )


@router.get("/llm/{decision_id}", response_class=HTMLResponse)
def llm_decision_detail(request: Request, decision_id: str):
    db = SessionLocal()

    decision = (
        db.query(LLMDecision)
        .filter(LLMDecision.id == decision_id)
        .first()
    )

    db.close()

    if not decision:
        return HTMLResponse("Decision not found", status_code=404)

    return templates.TemplateResponse(
        "llm_detail.html",
        {
            "request": request,
            "d": decision
        }
    )


@router.get("/stats/jobs-per-day", response_class=JSONResponse)
def jobs_per_day():
    db = SessionLocal()

    results = (
        db.query(
            cast(Job.created_at, Date).label("day"),
            func.count(Job.id).label("count")
        )
        .group_by("day")
        .order_by("day")
        .all()
    )

    db.close()

    return [
        {"day": str(r.day), "count": r.count}
        for r in results
    ]

@router.get("/charts", response_class=HTMLResponse)
def charts_view(request: Request):
    return templates.TemplateResponse(
        "charts.html",
        {"request": request}
    )
