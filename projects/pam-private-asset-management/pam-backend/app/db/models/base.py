from sqlalchemy.ext.declarative import declarative_base

# Base class for all models to inherit from.
# It's in a separate file to prevent circular import issues.
Base = declarative_base()
