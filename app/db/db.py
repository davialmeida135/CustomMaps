from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from pathlib import Path

Base = declarative_base()

class PinType(Base):
    __tablename__ = 'pin_types'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)  # Ensures name is unique
    color = Column(String, nullable=False, default="36aedc")
    style = Column(String, nullable=False, default="add_location")
    
    fields = relationship("Field", back_populates="pin_type", cascade="all, delete-orphan")
    pins = relationship("Pin", back_populates="pin_type", cascade="all, delete-orphan")

class Field(Base):
    __tablename__ = 'fields'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pin_type_id = Column(Integer, ForeignKey('pin_types.id', ondelete='CASCADE'), nullable=False)
    name = Column(String, nullable=False)
    field_type = Column(String, nullable=False)  # 'string', 'number', 'date'
    is_required = Column(Integer, default=0)  # 0 = False, 1 = True
    
    pin_type = relationship("PinType", back_populates="fields")
    field_values = relationship("FieldValue", back_populates="field", cascade="all, delete-orphan")

class Pin(Base):
    __tablename__ = 'pins'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pin_type_id = Column(Integer, ForeignKey('pin_types.id', ondelete='CASCADE'), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    pin_type = relationship("PinType", back_populates="pins")
    field_values = relationship("FieldValue", back_populates="pin", cascade="all, delete-orphan")

class FieldValue(Base):
    __tablename__ = 'field_values'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pin_id = Column(Integer, ForeignKey('pins.id', ondelete='CASCADE'), nullable=False)
    field_id = Column(Integer, ForeignKey('fields.id', ondelete='CASCADE'), nullable=False)
    value = Column(Text, nullable=False)  # Store value as text
    
    pin = relationship("Pin", back_populates="field_values")
    field = relationship("Field", back_populates="field_values")

# Create an SQLite database
base_dir = Path(__file__).resolve().parent
db_path = base_dir / 'map_pins.db'
engine = create_engine(f'sqlite:///{db_path}')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def get_session():
    return Session()
