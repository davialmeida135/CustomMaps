"""
CRUD operations for the Custom Pins application.

This module provides functions for creating, reading, updating, and deleting pin types, pins, and their associated fields and values.

Functions:
    create_pin_type(name, fields, color=None, style="add_location"): Create a new pin type.
    get_all_pin_types(): Get all pin types.
    get_pin_type_by_name(name): Get a pin type by its name.
    add_pin(pin_type_name, latitude, longitude, field_values): Add a new pin.
    get_pin_by_id(pin_id): Get a pin by its ID.
    get_pins(pin_type_name): Get all pins of a specific pin type.
    get_all_pins(): Get all pins.
    update_pin(pin_id, updated_field_values): Update a pin.
    delete_pin(pin_id): Delete a pin.
    update_pin_type(pin_type_id, new_name=None, updated_fields=None, new_color=None, new_style=None): Update a pin type.
    delete_pin_type_and_pins(pin_type_name, map_id=0): Delete a pin type and all associated pins.
"""
from db.db import get_session
from db.db import PinType, Pin, Field, FieldValue

database = get_session()


def create_pin_type(name, fields, color=None, style="add_location"):
    """
    Create a new pin type.

    Args:
        name (str): The name of the pin type.
        fields (list): A list of fields associated with the pin type.
        color (str, optional): The color of the pin type. Defaults to None.
        style (str, optional): The style of the pin type. Defaults to "add_location".

    Returns:
        PinType: The created PinType object.
    """
    existing_pin_type = PinType.get_or_none(PinType.name == name)
    if existing_pin_type:
        raise ValueError(f"PinType '{name}' already exists.")
    
    pin_type = PinType.create(name=name, color=color, style=style)
    
    for field_name, field_type, is_required in fields:
        Field.create(pin_type=pin_type, name=field_name, field_type=field_type, is_required=is_required)
    
    return pin_type

def get_all_pin_types():
    """
    Get all pin types.

    Returns:
        list: A list of dictionaries representing all pin types.
    """
    pin_types = PinType.select()
    result = []
    
    for pin_type in pin_types:
        info = {
            'name': pin_type.name,
            'color': pin_type.color,
            'style': pin_type.style
        }
        result.append(info)
    
    return result

def get_pin_type_by_name(name):
    """
    Get a pin type by its name.

    Args:
        name (str): The name of the pin type.

    Returns:
        dict: A dictionary representing the pin type.
    """
    pin_type = PinType.get_or_none(PinType.name == name)
    if not pin_type:
        raise ValueError(f"PinType '{name}' does not exist.")
    
    result = {
        "name": pin_type.name,
        "color": pin_type.color,
        "style": pin_type.style,
        "fields": []
    }
    
    for field in pin_type.fields:
        result["fields"].append({
            "name": field.name,
            "field_type": field.field_type,
            "is_required": bool(field.is_required)
        })
    
    return result

def add_pin(pin_type_name, latitude, longitude, field_values):
    """
    Add a new pin.

    Args:
        pin_type_name (str): The name of the pin type.
        latitude (float): The latitude of the pin.
        longitude (float): The longitude of the pin.
        field_values (dict): A dictionary of field values for the pin.

    Returns:
        Pin: The created Pin object.
    """
    pin_type = PinType.get_or_none(PinType.name == pin_type_name)
    if not pin_type:
        raise ValueError(f"PinType '{pin_type_name}' does not exist.")
    
    pin = Pin.create(pin_type=pin_type, latitude=latitude, longitude=longitude)
    
    for field_name, value in field_values.items():
        field = Field.get_or_none((Field.pin_type == pin_type) & (Field.name == field_name))
        if not field:
            raise ValueError(f"Field '{field_name}' does not exist for PinType '{pin_type_name}'.")
        
        FieldValue.create(pin=pin, field=field, value=value)
    
    return pin

def get_pin_by_id(pin_id):
    """
    Get a pin by its ID.

    Args:
        pin_id (int): The ID of the pin.

    Returns:
        dict: A dictionary representing the pin.
    """
    pin = Pin.get_or_none(Pin.id == pin_id)
    if not pin:
        raise ValueError(f"Pin with id '{pin_id}' does not exist.")
    
    pin_data = {
        "id": pin.id,
        "latitude": pin.latitude,
        "longitude": pin.longitude,
        "pin_type": pin.pin_type.name,
        "color": pin.pin_type.color,
        "style": pin.pin_type.style,
        "fields": {}
    }
    
    for field_value in pin.field_values:
        pin_data["fields"][field_value.field.name] = {
            "value": field_value.value,
            "type": field_value.field.field_type
        }
    
    return pin_data

def get_pins(pin_type_name):
    """
    Get all pins of a specific pin type.

    Args:
        pin_type_name (str): The name of the pin type.

    Returns:
        list: A list of dictionaries representing the pins.
    """
    pin_type = PinType.get_or_none(PinType.name == pin_type_name)
    if not pin_type:
        raise ValueError(f"PinType '{pin_type_name}' does not exist.")
    
    pins = Pin.select().where(Pin.pin_type == pin_type)
    result = []
    for pin in pins:
        pin_data = {
            "id": pin.id,
            "latitude": pin.latitude,
            "longitude": pin.longitude,
            "fields": {}
        }
        for field_value in pin.field_values:
            pin_data["fields"][field_value.field.name] = field_value.value
        result.append(pin_data)
    
    return result

def get_all_pins():
    """
    Get all pins.

    Returns:
        list: A list of dictionaries representing all pins.
    """
    pins = Pin.select()
    result = []
    for pin in pins:
        pin_data = {
            "id": pin.id,
            "pin_type": pin.pin_type.name,
            "latitude": pin.latitude,
            "longitude": pin.longitude,
            "color": pin.pin_type.color,
            "style": pin.pin_type.style,
            "fields": {}
        }
        for field_value in pin.field_values:
            pin_data["fields"][field_value.field.name] = field_value.value
        result.append(pin_data)
    
    return result

def update_pin(pin_id, updated_field_values):
    """
    Update a pin.

    Args:
        pin_id (int): The ID of the pin.
        updated_field_values (dict): A dictionary of updated field values for the pin.

    Returns:
        Pin: The updated Pin object.
    """
    pin = Pin.get_or_none(Pin.id == pin_id)
    if not pin:
        raise ValueError(f"Pin with ID '{pin_id}' does not exist.")
    
    for field_name, new_value in updated_field_values.items():
        field = Field.get_or_none((Field.pin_type == pin.pin_type) & (Field.name == field_name))
        if not field:
            raise ValueError(f"Field '{field_name}' does not exist for PinType ID '{pin.pin_type.id}'.")
        
        field_value = FieldValue.get_or_none((FieldValue.pin == pin) & (FieldValue.field == field))
        if field_value:
            field_value.value = new_value
            field_value.save()
        else:
            FieldValue.create(pin=pin, field=field, value=new_value)
    
    return pin

def delete_pin(pin_id):
    """
    Delete a pin.

    Args:
        pin_id (int): The ID of the pin.
    """
    pin = Pin.get_or_none(Pin.id == pin_id)
    if not pin:
        raise ValueError(f"Pin with ID '{pin_id}' does not exist.")
    
    pin.delete_instance(recursive=True)
    print(f"Pin {pin_id} deleted successfully.")

def update_pin_type(pin_type_id, new_name=None, updated_fields=None, new_color=None, new_style=None):
    """
    Update a pin type.

    Args:
        pin_type_id (int): The ID of the pin type.
        new_name (str, optional): The new name of the pin type. Defaults to None.
        updated_fields (list, optional): A list of updated fields for the pin type. Defaults to None.
        new_color (str, optional): The new color of the pin type. Defaults to None.
        new_style (str, optional): The new style of the pin type. Defaults to None.

    Returns:
        PinType: The updated PinType object.
    """
    pin_type = PinType.get_or_none(PinType.id == pin_type_id)
    if not pin_type:
        raise ValueError(f"PinType with ID '{pin_type_id}' does not exist.")
    
    if new_name:
        pin_type.name = new_name
    if new_color:
        pin_type.color = new_color
    if new_style:
        pin_type.style = new_style
    pin_type.save()
    
    if updated_fields is not None:
        existing_fields = {field.id: field for field in pin_type.fields}
        for field_data in updated_fields:
            field_id = field_data.get('id')
            if field_id and field_id in existing_fields:
                field = existing_fields[field_id]
                field.name = field_data['name']
                field.field_type = field_data['field_type']
                field.is_required = field_data['is_required']
                field.save()
            else:
                Field.create(pin_type=pin_type, name=field_data['name'], field_type=field_data['field_type'], is_required=field_data['is_required'])
        
        for field_id in set(existing_fields) - {field_data.get('id') for field_data in updated_fields}:
            existing_fields[field_id].delete_instance()
    
    return pin_type

def delete_pin_type_and_pins(pin_type_name, map_id=0):
    """
    Delete a pin type and all associated pins.

    Args:
        pin_type_name (str): The name of the pin type.
        map_id (int, optional): The ID of the map. Defaults to 0.
    """
    pin_type = PinType.get_or_none(PinType.name == pin_type_name)
    if not pin_type:
        raise ValueError(f"PinType with ID '{pin_type_name}' does not exist.")
    
    # Delete all pins of this type
    pins = Pin.select().where(Pin.pin_type == pin_type)
    for pin in pins:
        pin.delete_instance(recursive=True)
    
    # Delete the pin type
    pin_type.delete_instance()
    print(f"PinType {pin_type_name} and all associated pins deleted successfully.")