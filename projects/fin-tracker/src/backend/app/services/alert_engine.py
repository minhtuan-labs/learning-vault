from __future__ import annotations

from datetime import datetime

from app.db.session import SessionLocal
from app.models.alert import Alert
from app.models.company import Company
from app.models.financial import FinancialData, FinancialPeriod
from app.services.pdf_extractor import BANK_KEYWORDS, _is_bank


_BANK_REVENUE_KEYS = [
    "Tổng thu nhập hoạt động",
    "TOI",
    "Tổng thu nhập",
    "Thu nhập hoạt động",
]
_KQKD_REVENUE_KEYS = ["Doanh thu thuần", "Doanh thu", "Tổng doanh thu"]
_KQKD_PROFIT_KEYS = [
    "Lợi nhuận sau thuế",
    "Lợi nhuận ròng",
    "Lợi nhuận sau thuế TNDN",
    "Lợi nhuận sau thuế thu nhập doanh nghiệp",
]


def _match(metrics: dict[str, float], keys: list[str]) -> float | None:
    for key in keys:
        for m_name, m_val in metrics.items():
            if key.lower() in m_name.lower():
                return m_val
    return None


def _get_metrics(db, period_id: int) -> dict[str, float]:
    rows = db.execute(
        FinancialData.__table__.select().where(FinancialData.period_id == period_id)
    ).all()
    return {r.metric_name: float(r.metric_value) for r in rows}


def _pct_change(new_val: float | None, old_val: float | None) -> float | None:
    if new_val is None or old_val is None or old_val == 0:
        return None
    return (new_val - old_val) / abs(old_val) * 100


class AlertEngine:
    def check_alerts(self, period_id: int) -> list[Alert]:
        db = SessionLocal()
        alerts = []
        try:
            period = db.get(FinancialPeriod, period_id)
            if not period:
                return alerts

            company = db.get(Company, period.company_id)
            if not company:
                return alerts

            is_bank_entity = _is_bank(company.industry)

            revenue_keys = _BANK_REVENUE_KEYS if is_bank_entity else _KQKD_REVENUE_KEYS
            profit_keys = _KQKD_PROFIT_KEYS

            current_metrics = _get_metrics(db, period_id)

            # Find the comparison period (year-over-year for better context)
            prev_stmt = (
                db.query(FinancialPeriod)
                .filter(
                    FinancialPeriod.company_id == period.company_id,
                    FinancialPeriod.period_type == period.period_type,
                )
                .order_by(FinancialPeriod.year.desc(), FinancialPeriod.quarter.desc())
                .all()
            )
            prev_period = None
            for p in prev_stmt:
                if p.id != period.id:
                    # For yearly: compare with previous year
                    if not period.quarter and not p.quarter and p.year == period.year - 1:
                        prev_period = p
                        break
                    # For quarterly: compare with same quarter of previous year (better context)
                    if period.quarter and p.quarter and p.quarter == period.quarter and p.year == period.year - 1:
                        prev_period = p
                        break

            prev_metrics = {}
            if prev_period:
                prev_metrics = _get_metrics(db, prev_period.id)

            period_label = (
                f"Q{period.quarter}/{period.year}" if period.quarter else f"Năm {period.year}"
            )
            prev_label = (
                f"Q{prev_period.quarter}/{prev_period.year}"
                if prev_period and prev_period.quarter
                else (f"Năm {prev_period.year}" if prev_period else "")
            )

            cur_revenue = _match(current_metrics, revenue_keys)
            prev_revenue = _match(prev_metrics, revenue_keys) if prev_metrics else None
            cur_profit = _match(current_metrics, profit_keys)
            prev_profit = _match(prev_metrics, profit_keys) if prev_metrics else None

            rev_change = _pct_change(cur_revenue, prev_revenue)
            profit_change = _pct_change(cur_profit, prev_profit)

            TO_BILLION = 1_000_000

            if rev_change is not None and rev_change < -20:
                alerts.append(
                    Alert(
                        company_id=period.company_id,
                        period_id=period_id,
                        alert_type="revenue_drop",
                        severity="medium",
                        description=f"Doanh thu {period_label} giảm {abs(rev_change):.1f}% so với {prev_label}",
                        is_read=False,
                        created_at=datetime.now(),
                    )
                )

            if cur_profit is not None and cur_profit < 0:
                alerts.append(
                    Alert(
                        company_id=period.company_id,
                        period_id=period_id,
                        alert_type="negative_profit",
                        severity="high",
                        description=f"Lợi nhuận sau thuế âm {cur_profit / TO_BILLION:.1f} tỷ VND trong {period_label}",
                        is_read=False,
                        created_at=datetime.now(),
                    )
                )

            debt_ratio_cur = _match(current_metrics, ["Nợ phải trả"])
            asset_cur = _match(current_metrics, ["Tổng tài sản"])
            debt_ratio_prev = _match(prev_metrics, ["Nợ phải trả"]) if prev_metrics else None
            asset_prev = _match(prev_metrics, ["Tổng tài sản"]) if prev_metrics else None

            if (
                debt_ratio_cur
                and asset_cur
                and debt_ratio_prev
                and asset_prev
                and asset_cur > 0
                and asset_prev > 0
            ):
                ratio_cur = debt_ratio_cur / asset_cur
                ratio_prev = debt_ratio_prev / asset_prev
                debt_change = _pct_change(ratio_cur, ratio_prev)
                if debt_change is not None and debt_change > 30:
                    alerts.append(
                        Alert(
                            company_id=period.company_id,
                            period_id=period_id,
                            alert_type="debt_surge",
                            severity="low",
                            description=f"Tỷ lệ nợ/tài sản tăng {debt_change:.1f}% so với {prev_label}",
                            is_read=False,
                            created_at=datetime.now(),
                        )
                    )

            if rev_change is not None and rev_change > 0 and profit_change is not None and profit_change < -10:
                alerts.append(
                    Alert(
                        company_id=period.company_id,
                        period_id=period_id,
                        alert_type="cost_anomaly",
                        severity="medium",
                        description=f"Doanh thu tăng {rev_change:.1f}% nhưng lợi nhuận giảm {abs(profit_change):.1f}% — chi phí có dấu hiệu bất thường",
                        is_read=False,
                        created_at=datetime.now(),
                    )
                )

            if is_bank_entity:
                npl_cur = _match(current_metrics, ["Nợ xấu", "Tỷ lệ nợ xấu"])
                npl_prev = _match(prev_metrics, ["Nợ xấu", "Tỷ lệ nợ xấu"]) if prev_metrics else None

                if npl_cur is not None and npl_prev is not None and npl_prev > 0:
                    npl_change = _pct_change(npl_cur, npl_prev)
                    if npl_change is not None and npl_change > 50:
                        alerts.append(
                            Alert(
                                company_id=period.company_id,
                                period_id=period_id,
                                alert_type="npl_surge",
                                severity="high",
                                description=f"Tỷ lệ nợ xấu tăng từ {npl_prev:.1f}% lên {npl_cur:.1f}%",
                                is_read=False,
                                created_at=datetime.now(),
                            )
                        )

            saved_alerts = []
            for alert in alerts:
                db.add(alert)
                saved_alerts.append(alert)
            db.commit()

            # Return descriptions for immediate use
            return [a.description for a in saved_alerts]

        except Exception as e:
            print(f"Alert check error: {e}")
            db.rollback()
            return alerts
        finally:
            db.close()
