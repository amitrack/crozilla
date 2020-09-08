from sqlalchemy import (
    Integer, String, DateTime, Numeric)
from sqlalchemy import create_engine, Column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def db_connect(connection_string):
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(connection_string)


def create_table(engine):
    Base.metadata.create_all(engine)


class Listing(Base):
    __tablename__ = "crozilla_listings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    crozilla_id = Column(String, primary_key=True, unique=True)
    title = Column(String)
    url = Column(String)
    city = Column(String)
    price = Column(Numeric)
    currency = Column(String)
    rooms = Column(Numeric)
    living_area = Column(Numeric)
    zip_code = Column(String)
    transaction_type = Column(String)
    district = Column(String)
    federal_state = Column(String)
    country = Column(String)
    address = Column(String)
    broker_url = Column(String)
    image_src = Column(String)
    type = Column(String)
    broker = Column(String)
    first_found = Column(DateTime)
    found_last = Column(DateTime)
    crawl_id = Column(String)
    area = Column(Numeric)
    balcony = Column(String)
    garden = Column(String)
    kitchen = Column(String)
    cellar = Column(String)
