from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.models.ai_analysis import AIAnalysis
from app.models.financial import FinancialPeriod
from app.schemas.analysis import AIAnalysisResponse
from app.services.ai_analyzer import AIAnalyzer

router = APIRouter()
_analyzer = AIAnalyzer()


@router.get("/companies/{company_id}/analysis", response_model=list[AIAnalysisResponse])
def list_analysis(company_id: int, db: Session = Depends(get_db)):
    rows = (
        db.execute(
            select(
                AIAnalysis.id,
                AIAnalysis.company_id,
                AIAnalysis.period_id,
                FinancialPeriod.year,
                FinancialPeriod.quarter,
                AIAnalysis.analysis_text,
                AIAnalysis.analysis_html,
                AIAnalysis.created_at,
            )
            .join(FinancialPeriod, FinancialPeriod.id == AIAnalysis.period_id)
            .where(AIAnalysis.company_id == company_id)
            .order_by(desc(AIAnalysis.created_at))
        )
        .all()
    )

    result = []
    for r in rows:
        period_label = f"Q{r.quarter}/{r.year}" if r.quarter else f"Năm {r.year}"
        result.append(
            AIAnalysisResponse(
                id=r.id,
                company_id=r.company_id,
                period_id=r.period_id,
                period_label=period_label,
                analysis_text=r.analysis_text,
                analysis_html=r.analysis_html,
                created_at=r.created_at,
            )
        )
    return result


@router.post("/periods/{period_id}/analyze")
def trigger_analysis(period_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    period = db.get(FinancialPeriod, period_id)
    if not period:
        raise HTTPException(404, "Period not found")

    existing = db.execute(
        select(AIAnalysis).where(AIAnalysis.period_id == period_id)
    ).scalar_one_or_none()
    if existing:
        return {"message": "Analysis already exists", "analysis_id": existing.id}

    background_tasks.add_task(_analyzer.analyze_period, period_id)
    return {"message": "Analysis started"}
