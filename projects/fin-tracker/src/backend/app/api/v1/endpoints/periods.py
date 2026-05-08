from fastapi import APIRouter, BackgroundTasks, Body, Depends, File, Form, HTTPException, Response, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_session
from app.models.financial import FinancialPeriod, ReportFile, ReportTypeEnum
from app.models.user import User
from app.schemas.financial import (
    ExtractRequest,
    FinancialDataResponse,
    FinancialDataUpdate,
    ReportFileResponse,
)
from app.services.alert_engine import AlertEngine
from app.services.ai_analyzer import AIAnalyzer
from app.services.period_service import PeriodService
from app.services.settings_service import is_enabled

router = APIRouter(prefix="/periods", tags=["periods"])
_analyzer = AIAnalyzer()


@router.get("/{period_id}/files", response_model=list[ReportFileResponse])
def list_period_files(period_id: int, db: Session = Depends(get_db_session), _current_user: User = Depends(get_current_user)):
    svc = PeriodService(db)
    svc.get_period(period_id)
    rows = list(
        db.scalars(
            select(ReportFile)
            .where(ReportFile.period_id == period_id)
            .order_by(ReportFile.uploaded_at.desc())
        ).all()
    )
    return [ReportFileResponse.model_validate(r) for r in rows]


@router.post("/{period_id}/upload", response_model=ReportFileResponse, status_code=status.HTTP_201_CREATED)
def upload_report_pdf(
    period_id: int,
    file: UploadFile = File(...),
    report_type: ReportTypeEnum = Form(...),
    db: Session = Depends(get_db_session),
    _current_user: User = Depends(get_current_user),
):
    svc = PeriodService(db)
    rf = svc.save_pdf_upload(period_id, file, report_type)
    return ReportFileResponse.model_validate(rf)


@router.get("/{period_id}/files/{file_id}")
def download_report_pdf(
    period_id: int,
    file_id: int,
    db: Session = Depends(get_db_session),
    _current_user: User = Depends(get_current_user),
):
    svc = PeriodService(db)
    rf = svc.get_report_file(period_id, file_id)
    path = svc.resolve_file_abs_path(rf)
    return FileResponse(
        path,
        media_type="application/pdf",
        filename=rf.file_name,
        content_disposition_type="inline",
    )


@router.post("/{period_id}/extract")
def extract_financial_data(
    period_id: int,
    background_tasks: BackgroundTasks,
    body: ExtractRequest | None = Body(default=None),
    db: Session = Depends(get_db_session),
    _current_user: User = Depends(get_current_user),
):
    if not is_enabled(db, "ai_extraction_enabled"):
        raise HTTPException(status_code=403, detail="Trích xuất AI đang bị tắt trong cài đặt hệ thống.")
    svc = PeriodService(db)
    payload = body or ExtractRequest()
    rows, entity_type = svc.extract_from_file(period_id, payload)

    alert_engine = AlertEngine()
    if is_enabled(db, "alert_enabled"):
        background_tasks.add_task(alert_engine.check_alerts, period_id)

    period = db.get(FinancialPeriod, period_id)
    if period and is_enabled(db, "ai_analysis_enabled"):
        background_tasks.add_task(_analyzer.analyze_company, period.company_id)

    return {
        "entity_type": entity_type,
        "metrics": [FinancialDataResponse.model_validate(r).model_dump() for r in rows],
    }


@router.get("/{period_id}/data", response_model=list[FinancialDataResponse])
def list_financial_data(period_id: int, db: Session = Depends(get_db_session), _current_user: User = Depends(get_current_user)):
    svc = PeriodService(db)
    rows = svc.list_financial_data(period_id)
    return [FinancialDataResponse.model_validate(r) for r in rows]


@router.put("/{period_id}/data/{metric_id}", response_model=FinancialDataResponse)
def update_financial_metric(
    period_id: int,
    metric_id: int,
    payload: FinancialDataUpdate,
    db: Session = Depends(get_db_session),
    _current_user: User = Depends(get_current_user),
):
    svc = PeriodService(db)
    row = svc.update_metric(period_id, metric_id, payload)
    return FinancialDataResponse.model_validate(row)


@router.post("/{period_id}/verify", status_code=status.HTTP_200_OK)
def verify_period_data(period_id: int, db: Session = Depends(get_db_session), _current_user: User = Depends(get_current_user)):
    svc = PeriodService(db)
    count = svc.verify_all(period_id)
    return {"verified_count": count, "message": "Đã xác nhận toàn bộ số liệu trong kỳ."}


@router.delete("/{period_id}/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report_file(
    period_id: int,
    file_id: int,
    db: Session = Depends(get_db_session),
    _current_user: User = Depends(get_current_user),
):
    svc = PeriodService(db)
    svc.delete_file(period_id, file_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)