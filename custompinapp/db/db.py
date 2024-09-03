from peewee import (
    Model, SqliteDatabase, IntegerField, FloatField, TextField, ForeignKeyField, CharField
)
import os

# Define the database path and initialize the database
path = os.path.abspath(__file__)
path = os.path.dirname(path)
path = os.path.dirname(path)
path = os.path.dirname(path)
db_path = os.path.join(path, 'map_pins.db')
database = SqliteDatabase(db_path)
print(db_path)

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

# Create the "Default" pin type with name and date fields
def create_default_pin_type():
    default_pin_type, created = PinType.get_or_create(
        name="Default",
        defaults={"color": "36aedc", "style": "add_location"}
    )
    if created:
        Field.create(pin_type=default_pin_type, name="Name", field_type="string", is_required=1)
        Field.create(pin_type=default_pin_type, name="Date", field_type="date", is_required=1)
        print("Default pin type and fields created.")
    else:
        print("Default pin type already exists.")

create_default_pin_type()
def get_session():
    return database
