"""
Database models and initialization for the Custom Pins application.

This module defines the database models and initializes the SQLite database.

Classes:
    BaseModel: Base model class for all database models.
    PinType: Model class for pin types.
    Field: Model class for fields associated with pin types.
    Pin: Model class for pins.
    FieldValue: Model class for field values associated with pins.

Functions:
    create_default_pin_type(): Create the default pin type with name and date fields.
"""
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
    """
    Base model class for all database models.

    Attributes:
        Meta: Meta class to define the database.
    """
    class Meta:
        database = database

class PinType(BaseModel):
    """
    Model class for pin types.

    Attributes:
        name (CharField): The name of the pin type.
        color (CharField): The color of the pin type.
        style (CharField): The style of the pin type.
    """
    name = CharField(unique=True, null=False)  # Ensures name is unique
    color = CharField(default="36aedc", null=False)
    style = CharField(default="add_location", null=False)

class Field(BaseModel):
    """
    Model class for fields associated with pin types.

    Attributes:
        pin_type (ForeignKeyField): The pin type associated with the field.
        name (CharField): The name of the field.
        field_type (CharField): The type of the field ('string', 'number', 'date').
        is_required (IntegerField): Whether the field is required (0 = False, 1 = True).
    """
    pin_type = ForeignKeyField(PinType, backref='fields', on_delete='CASCADE')
    name = CharField(null=False)
    field_type = CharField(null=False)  # 'string', 'number', 'date'
    is_required = IntegerField(default=0)  # 0 = False, 1 = True

class Pin(BaseModel):
    """
    Model class for pins.

    Attributes:
        pin_type (ForeignKeyField): The pin type associated with the pin.
        latitude (FloatField): The latitude of the pin.
        longitude (FloatField): The longitude of the pin.
    """
    pin_type = ForeignKeyField(PinType, backref='pins', on_delete='CASCADE')
    latitude = FloatField(null=False)
    longitude = FloatField(null=False)

class FieldValue(BaseModel):
    """
    Model class for field values associated with pins.

    Attributes:
        pin (ForeignKeyField): The pin associated with the field value.
        field (ForeignKeyField): The field associated with the field value.
        value (TextField): The value of the field stored as text.
    """
    pin = ForeignKeyField(Pin, backref='field_values', on_delete='CASCADE')
    field = ForeignKeyField(Field, backref='field_values', on_delete='CASCADE')
    value = TextField(null=False)  # Store value as text

# Create tables
database.connect()
database.create_tables([PinType, Field, Pin, FieldValue])

# Create the "Default" pin type with name and date fields
def create_default_pin_type():
    """
    Creates the default pin type with predefined fields if it doesn't already exist.

    This function checks if a pin type named "Default" exists. If not, it creates the pin type
    and adds two fields: "Name" (string) and "Date" (date), both of which are required.
    """
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
    """
    Retrieves the current database session.

    This function returns the current database connection, which can be used to perform
    database operations within a session context.

    Returns:
        SqliteDatabase: The current database connection.
    """
    return database
