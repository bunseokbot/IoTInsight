"""Database session manager."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///iotinsight.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()
