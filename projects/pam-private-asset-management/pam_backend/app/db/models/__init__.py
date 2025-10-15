# This file makes the 'models' folder a Python package.
# It imports all the models so they are registered with SQLAlchemy's Base
# and can be easily imported from other parts of the application.

from .base import Base
from .user import User
from .asset import Asset, StockDetail, SavingDetail, AssetTypeEnum
from .transaction import Transaction, TransactionTypeEnum
