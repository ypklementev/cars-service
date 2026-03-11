from sqlalchemy import Column, Integer, String
from .db import Base


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True)
    brand = Column(String)
    model = Column(String)
    year = Column(Integer)
    price = Column(Integer)
    color = Column(String)
    url = Column(String, unique=True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)