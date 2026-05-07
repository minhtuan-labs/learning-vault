"""Migration: Restructure ai_analysis to one-per-company with status tracking"""
from sqlalchemy import text
from app.db.session import engine


def upgrade():
    with engine.begin() as conn:
        # Ensure enum type exists for status column
        conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_type WHERE typname = 'analysis_status'
                ) THEN
                    CREATE TYPE analysis_status AS ENUM ('PENDING', 'COMPLETED');
                END IF;
            END
            $$;
        """))

        # Check if new columns exist
        result = conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'ai_analysis'
        """)).fetchall()
        existing_cols = {r[0] for r in result}

        if 'status' not in existing_cols:
            # Add new columns
            conn.execute(text(
                "ALTER TABLE ai_analysis ADD COLUMN status analysis_status NOT NULL DEFAULT 'PENDING'"
            ))
            conn.execute(text(
                "ALTER TABLE ai_analysis ADD COLUMN updated_at TIMESTAMP WITHOUT TIME ZONE"
            ))
            print("Added status and updated_at columns")
        else:
            # If status existed as text/varchar, convert safely to enum with uppercase values
            conn.execute(text(
                "ALTER TABLE ai_analysis ALTER COLUMN status TYPE analysis_status USING UPPER(status)::analysis_status"
            ))
            conn.execute(text(
                "ALTER TABLE ai_analysis ALTER COLUMN status SET DEFAULT 'PENDING'"
            ))

        # Migrate data: keep only one analysis per company (most recent)
        conn.execute(text("""
            DELETE FROM ai_analysis a
            USING (
                SELECT company_id, MAX(created_at) as max_created
                FROM ai_analysis
                GROUP BY company_id
                HAVING COUNT(*) > 1
            ) dup
            WHERE a.company_id = dup.company_id
            AND a.created_at < dup.max_created
        """))
        print("Removed duplicate analyses, keeping most recent per company")

        # Drop period_id column if it exists
        if 'period_id' in existing_cols:
            # First drop the foreign key constraint
            conn.execute(text(
                "ALTER TABLE ai_analysis DROP CONSTRAINT IF EXISTS ai_analysis_period_id_fkey"
            ))
            conn.execute(text(
                "ALTER TABLE ai_analysis DROP COLUMN IF EXISTS period_id"
            ))
            print("Dropped period_id column")

        # Add unique constraint on company_id if not exists
        result = conn.execute(text("""
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'ai_analysis'
            AND constraint_type = 'UNIQUE'
            AND constraint_name LIKE '%company_id%'
        """))
        if not result.first():
            conn.execute(text(
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_ai_analysis_company_id ON ai_analysis (company_id)"
            ))
            print("Added unique index on company_id")

        # Set updated_at = created_at for existing rows
        conn.execute(text(
            "UPDATE ai_analysis SET updated_at = created_at WHERE updated_at IS NULL"
        ))

        # Set status to completed for existing rows
        conn.execute(text(
            "UPDATE ai_analysis SET status = 'COMPLETED' WHERE status = 'PENDING' AND analysis_text != ''"
        ))

        print("Migration completed successfully")


if __name__ == "__main__":
    upgrade()
