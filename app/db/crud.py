# crud.py
from db.db import get_session
from db.db import PinType, Pin, Field, FieldValue

database = get_session()

def create_pin_type(name, fields, color=None, style="add_location"):
    existing_pin_type = PinType.get_or_none(PinType.name == name)
    if existing_pin_type:
        raise ValueError(f"PinType '{name}' already exists.")
    
    pin_type = PinType.create(name=name, color=color, style=style)
    
    for field_name, field_type, is_required in fields:
        Field.create(pin_type=pin_type, name=field_name, field_type=field_type, is_required=is_required)
    
    return pin_type

def get_all_pin_types():
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
    pin = Pin.get_or_none(Pin.id == pin_id)
    if not pin:
        raise ValueError(f"Pin with ID '{pin_id}' does not exist.")
    
    pin.delete_instance(recursive=True)
    print(f"Pin {pin_id} deleted successfully.")

def update_pin_type(pin_type_id, new_name=None, updated_fields=None, new_color=None, new_style=None):
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