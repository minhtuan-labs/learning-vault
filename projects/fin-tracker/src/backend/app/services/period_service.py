from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import delete, desc, nulls_last, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.financial import (
    FinancialData,
    FinancialPeriod,
    PeriodTypeEnum,
    ReportFile,
    ReportTypeEnum,
)
from app.schemas.financial import (
    ExtractRequest,
    FinancialDataUpdate,
    FinancialPeriodCreate,
)
from app.services.company_service import CompanyService
from app.services import pdf_extractor


class PeriodService:
    def __init__(self, db: Session):
        self.db = db

    def _upload_root(self) -> Path:
        root = Path(settings.upload_dir)
        root.mkdir(parents=True, exist_ok=True)
        return root

    def _abs_path(self, relative: str) -> Path:
        return self._upload_root() / relative

    def create_period(self, company_id: int, payload: FinancialPeriodCreate) -> FinancialPeriod:
        CompanyService(self.db).get_company(company_id)
        if payload.period_type == PeriodTypeEnum.Q:
            if payload.quarter is None or payload.quarter not in (1, 2, 3, 4):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Kỳ quý (quarter) bắt buộc từ 1 đến 4 khi period_type là Q.",
                )
        elif payload.period_type == PeriodTypeEnum.Y:
            if payload.quarter is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Báo cáo cả năm không được gán quarter.",
                )

        period = FinancialPeriod(
            company_id=company_id,
            year=payload.year,
            quarter=payload.quarter,
            period_type=payload.period_type,
        )
        self.db.add(period)
        self.db.commit()
        self.db.refresh(period)
        return period

    def list_periods(self, company_id: int) -> list[FinancialPeriod]:
        CompanyService(self.db).get_company(company_id)
        stmt = (
            select(FinancialPeriod)
            .where(FinancialPeriod.company_id == company_id)
            .order_by(
                FinancialPeriod.year.desc(),
                nulls_last(desc(FinancialPeriod.quarter)),
                FinancialPeriod.created_at.desc(),
            )
        )
        return list(self.db.scalars(stmt).all())

    def get_period(self, period_id: int) -> FinancialPeriod:
        period = self.db.get(FinancialPeriod, period_id)
        if not period:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy kỳ báo cáo.")
        return period

    def save_pdf_upload(
        self,
        period_id: int,
        file: UploadFile,
        report_type: ReportTypeEnum,
    ) -> ReportFile:
        period = self.get_period(period_id)
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chỉ chấp nhận file PDF.",
            )
        max_bytes = settings.max_upload_mb * 1024 * 1024
        rel_dir = Path(str(period_id))
        self._upload_root().joinpath(rel_dir).mkdir(parents=True, exist_ok=True)
        safe_name = f"{uuid.uuid4().hex}.pdf"
        rel_path = rel_dir / safe_name
        abs_path = self._abs_path(str(rel_path))

        size = 0
        try:
            with abs_path.open("wb") as out:
                while True:
                    chunk = file.file.read(1024 * 1024)
                    if not chunk:
                        break
                    size += len(chunk)
                    if size > max_bytes:
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"File vượt quá {settings.max_upload_mb}MB.",
                        )
                    out.write(chunk)
        except HTTPException:
            if abs_path.exists():
                abs_path.unlink(missing_ok=True)
            raise

        rf = ReportFile(
            period_id=period.id,
            report_type=report_type,
            file_name=file.filename,
            file_path=str(rel_path).replace("\\", "/"),
            file_size=size,
        )
        self.db.add(rf)
        self.db.commit()
        self.db.refresh(rf)
        return rf

    def get_report_file(self, period_id: int, file_id: int) -> ReportFile:
        self.get_period(period_id)
        rf = self.db.get(ReportFile, file_id)
        if not rf or rf.period_id != period_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy file.")
        return rf

    def resolve_file_abs_path(self, rf: ReportFile) -> Path:
        p = self._abs_path(rf.file_path)
        if not p.is_file():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File không tồn tại trên máy chủ.")
        return p

    def extract_from_file(self, period_id: int, body: ExtractRequest) -> tuple[list[FinancialData], str]:
        period = self.get_period(period_id)
        if not settings.anthropic_api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Chưa cấu hình ANTHROPIC_API_KEY.",
            )

        company = CompanyService(self.db).get_company(period.company_id)
        company_industry = company.industry if company else None

        if body.file_id:
            rf = self.get_report_file(period_id, body.file_id)
        else:
            stmt = (
                select(ReportFile)
                .where(ReportFile.period_id == period_id)
                .order_by(ReportFile.uploaded_at.desc())
                .limit(1)
            )
            rf = self.db.scalar(stmt)
            if not rf:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Chưa có file PDF nào cho kỳ này.",
                )

        abs_pdf = self.resolve_file_abs_path(rf)
        try:
            raw = pdf_extractor.extract_financial_json_from_pdf(
                abs_pdf,
                api_key=settings.anthropic_api_key,
                model=settings.anthropic_model,
                default_report_type=rf.report_type.value,
                company_industry=company_industry,
            )
            rt_str, metrics, entity_type = pdf_extractor.normalize_metrics(raw)
        except FileNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e
        except Exception as e:  # noqa: BLE001
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Lỗi khi gọi AI trích xuất: {e!s}",
            ) from e

        try:
            report_type = ReportTypeEnum(rt_str)
        except ValueError:
            report_type = rf.report_type

        self.db.execute(
            delete(FinancialData).where(
                FinancialData.period_id == period.id,
                FinancialData.report_type == report_type,
            )
        )
        rows: list[FinancialData] = []
        for m in metrics:
            row = FinancialData(
                period_id=period.id,
                report_type=report_type,
                metric_name=m["name"],
                metric_value=m["value"],
                unit=m["unit"],
                is_verified=False,
            )
            self.db.add(row)
            rows.append(row)
        self.db.commit()
        for r in rows:
            self.db.refresh(r)
        return rows, entity_type

    def list_financial_data(self, period_id: int) -> list[FinancialData]:
        self.get_period(period_id)
        stmt = (
            select(FinancialData)
            .where(FinancialData.period_id == period_id)
            .order_by(FinancialData.report_type, FinancialData.metric_name)
        )
        return list(self.db.scalars(stmt).all())

    def update_metric(self, period_id: int, metric_id: int, payload: FinancialDataUpdate) -> FinancialData:
        self.get_period(period_id)
        row = self.db.get(FinancialData, metric_id)
        if not row or row.period_id != period_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy chỉ số.")
        row.metric_value = payload.metric_value
        if payload.unit is not None:
            row.unit = payload.unit
        row.is_verified = False
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def verify_all(self, period_id: int) -> int:
        period = self.get_period(period_id)
        rows = self.list_financial_data(period.id)
        count = 0
        for r in rows:
            r.is_verified = True
            count += 1
            self.db.add(r)
        self.db.commit()
        return count

    def delete_file(self, period_id: int, file_id: int) -> None:
        period = self.get_period(period_id)
        rf = self.db.get(ReportFile, file_id)
        if not rf or rf.period_id != period_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy file.")
        abs_path = self._abs_path(rf.file_path)
        if abs_path.exists():
            abs_path.unlink(missing_ok=True)
        report_type = rf.report_type
        self.db.delete(rf)
        self.db.execute(
            delete(FinancialData).where(
                FinancialData.period_id == period_id,
                FinancialData.report_type == report_type,
            )
        )
        self.db.commit()

    def delete_period(self, company_id: int, period_id: int) -> None:
        period = self.get_period(period_id)
        if period.company_id != company_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy kỳ báo cáo.")
        files = list(
            self.db.scalars(
                select(ReportFile).where(ReportFile.period_id == period_id)
            ).all()
        )
        for rf in files:
            abs_path = self._abs_path(rf.file_path)
            if abs_path.exists():
                abs_path.unlink(missing_ok=True)
        self.db.delete(period)
        self.db.commit()
