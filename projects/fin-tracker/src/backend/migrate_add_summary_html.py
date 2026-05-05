"""Migration: Add summary_html column to company_summaries table"""
from sqlalchemy import text
from app.db.session import engine

with engine.begin() as conn:
    # Check if column exists
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'company_summaries' 
        AND column_name = 'summary_html'
    """))
    
    if result.first() is None:
        conn.execute(text("ALTER TABLE company_summaries ADD COLUMN summary_html TEXT NOT NULL DEFAULT ''"))
        print("Added summary_html column to company_summaries")
    else:
        print("Column summary_html already exists")
