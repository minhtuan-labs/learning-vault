from __future__ import annotations

import markdown_it
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.models.ai_analysis import AIAnalysis, AnalysisStatus
from app.models.company import Company
from app.schemas.analysis import AIAnalysisResponse
from app.services.ai_analyzer import AIAnalyzer

router = APIRouter(prefix="/analysis", tags=["analysis"])
_analyzer = AIAnalyzer()
_md = markdown_it.MarkdownIt("commonmark", {"breaks": True, "html": True})
_md.enable(["table", "fence"])


def _ensure_html(text: str, html: str) -> str:
    """Convert markdown to HTML if html is empty."""
    if html and html.strip():
        return html
    if not text:
        return ""
    return _md.render(text)


@router.get("/companies/{company_id}/analysis", response_model=list[AIAnalysisResponse])
def list_analysis(company_id: int, db: Session = Depends(get_db_session)):
    # One analysis per company
    row = (
        db.execute(
            select(
                AIAnalysis.id,
                AIAnalysis.company_id,
                AIAnalysis.analysis_text,
                AIAnalysis.analysis_html,
                AIAnalysis.status,
                AIAnalysis.created_at,
                AIAnalysis.updated_at,
            )
            .where(AIAnalysis.company_id == company_id)
            .order_by(AIAnalysis.updated_at.desc(), AIAnalysis.created_at.desc(), AIAnalysis.id.desc())
        )
        .first()
    )

    if not row:
        return []

    analysis_html = _ensure_html(row.analysis_text, row.analysis_html)

    # Extract latest period from analysis text
    import re
    latest_label = "Tổng quan"
    # Look for patterns like "Q1/2026" or "2025" in the text
    period_match = re.search(r'(Q\d+/\d+|\d{4})', row.analysis_text)
    if period_match:
        period_str = period_match.group(1)
        if 'Q' in period_str:
            latest_label = period_str
        else:
            latest_label = f"Năm {period_str}"

    return [
        AIAnalysisResponse(
            id=row.id,
            company_id=row.company_id,
            period_id=0,  # kept for backward compat
            period_label=latest_label,
            analysis_text=row.analysis_text,
            analysis_html=analysis_html,
            status=row.status,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
    ]


@router.post("/companies/{company_id}/analyze")
def trigger_analysis(company_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db_session)):
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(404, "Company not found")

    # Upsert: mark as pending
    existing = db.query(AIAnalysis).filter(AIAnalysis.company_id == company_id).first()
    now = datetime.now()
    if existing:
        existing.status = AnalysisStatus.PENDING
        existing.updated_at = now
    else:
        existing = AIAnalysis(
            company_id=company_id,
            analysis_text="",
            analysis_html="",
            status=AnalysisStatus.PENDING,
            created_at=now,
            updated_at=now,
        )
        db.add(existing)
    db.commit()

    background_tasks.add_task(_analyzer.analyze_company, company_id)
    return {"message": "Analysis started", "analysis_id": existing.id}
