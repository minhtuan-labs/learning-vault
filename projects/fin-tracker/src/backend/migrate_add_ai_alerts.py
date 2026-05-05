"""
Migration: create ai_analysis and alerts tables
"""
from __future__ import annotations

from sqlalchemy import Connection, text


def migrate_up(conn: Connection) -> None:
    conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS ai_analysis (
                id SERIAL PRIMARY KEY,
                company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
                period_id INTEGER NOT NULL REFERENCES financial_periods(id) ON DELETE CASCADE,
                analysis_text TEXT NOT NULL,
                analysis_html TEXT NOT NULL DEFAULT '',
                created_at TIMESTAMP WITH TIME ZONE NOT NULL
            );
            """
        )
    )

    conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id SERIAL PRIMARY KEY,
                company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
                period_id INTEGER NOT NULL REFERENCES financial_periods(id) ON DELETE CASCADE,
                alert_type VARCHAR(50) NOT NULL,
                severity VARCHAR(20) NOT NULL,
                description TEXT NOT NULL,
                is_read BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL
            );
            """
        )
    )

    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_alerts_company ON alerts(company_id);"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_alerts_unread ON alerts(is_read) WHERE is_read = FALSE;"))


def migrate_down(conn: Connection) -> None:
    conn.execute(text("DROP TABLE IF EXISTS alerts;"))
    conn.execute(text("DROP TABLE IF EXISTS ai_analysis;"))
