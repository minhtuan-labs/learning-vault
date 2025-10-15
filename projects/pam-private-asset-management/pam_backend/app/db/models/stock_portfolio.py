from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base

class StockPortfolio(Base):
    __tablename__ = "stock_portfolios"
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    ticker = Column(String, index=True, nullable=False)
    target_price = Column(Float, nullable=True)
    stop_loss_price = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)

    asset = relationship("Asset", back_populates="stock_portfolios")
    trades = relationship("StockTrade", back_populates="portfolio", cascade="all, delete-orphan")
    __table_args__ = (UniqueConstraint('asset_id', 'ticker', name='_asset_ticker_uc'))
