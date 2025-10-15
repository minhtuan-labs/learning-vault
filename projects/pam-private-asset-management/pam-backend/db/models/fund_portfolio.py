from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base


class FundPortfolio(Base):
    __tablename__ = "fund_portfolios"
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    ticker = Column(String, index=True, nullable=False)
    notes = Column(Text, nullable=True)

    asset = relationship("Asset", back_populates="fund_portfolios")
    trades = relationship("FundTrade", back_populates="portfolio", cascade="all, delete-orphan")
    __table_args__ = (UniqueConstraint('asset_id', 'ticker', name='_fund_asset_ticker_uc'))

