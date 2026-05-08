from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Setting(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(String(500), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


DEFAULTS = {
    "ai_analysis_enabled": {
        "value": "true",
        "label": "Bật phân tích AI",
        "description": "Cho phép hệ thống gọi Anthropic API để phân tích BCTC, tóm tắt và so sánh doanh nghiệp. Tắt để tiết kiệm chi phí API.",
    },
    "ai_extraction_enabled": {
        "value": "true",
        "label": "Bật trích xuất AI",
        "description": "Cho phép AI tự động trích xuất số liệu từ PDF. Tắt thì phải nhập tay.",
    },
    "ai_summary_enabled": {
        "value": "true",
        "label": "Bật tóm tắt AI",
        "description": "Cho phép AI tự động tạo tóm tắt tình hình kinh doanh cho doanh nghiệp.",
    },
    "alert_enabled": {
        "value": "true",
        "label": "Bật cảnh báo",
        "description": "Tự động kiểm tra và tạo cảnh báo khi có chỉ số bất thường sau khi trích xuất BCTC.",
    },
}