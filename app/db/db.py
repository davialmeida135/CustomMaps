from peewee import (
    Model, SqliteDatabase, IntegerField, FloatField, TextField, ForeignKeyField, CharField
)
from pathlib import Path

# Define the database path and initialize the database
base_dir = Path(__file__).resolve().parent
db_path = base_dir / 'map_pins.db'
database = SqliteDatabase(db_path)

class BaseModel(Model):
    class Meta:
        database = database

class PinType(BaseModel):
    name = CharField(unique=True, null=False)  # Ensures name is unique
    color = CharField(default="36aedc", null=False)
    style = CharField(default="add_location", null=False)

class Field(BaseModel):
    pin_type = ForeignKeyField(PinType, backref='fields', on_delete='CASCADE')
    name = CharField(null=False)
    field_type = CharField(null=False)  # 'string', 'number', 'date'
    is_required = IntegerField(default=0)  # 0 = False, 1 = True

class Pin(BaseModel):
    pin_type = ForeignKeyField(PinType, backref='pins', on_delete='CASCADE')
    latitude = FloatField(null=False)
    longitude = FloatField(null=False)

class FieldValue(BaseModel):
    pin = ForeignKeyField(Pin, backref='field_values', on_delete='CASCADE')
    field = ForeignKeyField(Field, backref='field_values', on_delete='CASCADE')
    value = TextField(null=False)  # Store value as text

# Create tables
database.connect()
database.create_tables([PinType, Field, Pin, FieldValue])

def get_session():
    return database
