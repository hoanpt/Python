"""Routes: API endpoints & health check"""

from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from database import get_all_problems, get_all_submissions, get_stats

router = APIRouter()


@router.get("/api/problems")
async def api_problems():
    probs = get_all_problems()
    return JSONResponse([{
        "id": p["id"], "title": p.get("title"), "difficulty": p.get("difficulty"),
        "score_points": p.get("score_points"), "source_exam": p.get("source_exam", ""),
        "testcase_count": len(p.get("testcases", [])),
        "created_at": p.get("created_at"), "source": p.get("source", ""),
    } for p in probs])


@router.get("/api/submissions")
async def api_submissions():
    return JSONResponse(get_all_submissions())


@router.get("/health")
async def health():
    stats = get_stats()
    return {
        "status": "ok",
        "version": "3.0",
        "problems": stats["problems"],
        "submissions": stats["submissions"],
        "database": "sqlite",
        "time": datetime.now().isoformat(),
    }
