from __future__ import annotations

import re

import markdown_it
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_session
from app.models.ai_analysis import AIAnalysis, AnalysisStatus
from app.models.company import Company
from app.models.user import User
from app.schemas.analysis import AIAnalysisResponse
from app.services.ai_analyzer import AIAnalyzer
from app.services.settings_service import is_enabled

router = APIRouter(prefix="/analysis", tags=["analysis"])
_analyzer = AIAnalyzer()
_md = markdown_it.MarkdownIt("commonmark", {"breaks": True, "html": True})
_md.enable(["table", "fence"])


def _ensure_html(text: str, html: str) -> str:
    if html and html.strip():
        return html
    if not text:
        return ""
    return _md.render(text)


@router.get("/companies/{company_id}/analysis", response_model=list[AIAnalysisResponse])
def list_analysis(company_id: int, db: Session = Depends(get_db_session), _current_user: User = Depends(get_current_user)):
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

    latest_label = "Tổng quan"
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
            period_id=0,
            period_label=latest_label,
            analysis_text=row.analysis_text,
            analysis_html=analysis_html,
            status=row.status,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
    ]


@router.post("/companies/{company_id}/analyze")
def trigger_analysis(company_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db_session), _current_user: User = Depends(get_current_user)):
    if not is_enabled(db, "ai_analysis_enabled"):
        raise HTTPException(status_code=403, detail="Chức năng phân tích AI đang tắt. Vui lòng bật lại trong Cài đặt hệ thống.")
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(404, "Company not found")

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