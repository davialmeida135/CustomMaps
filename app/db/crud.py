# crud.py
from db.db import get_session
from db.db import PinType, Pin, Field, FieldValue

#from db import get_session
#from db import PinType, Pin, Field, FieldValue

session = get_session()

def create_pin_type(name, fields):
    pin_type = PinType(name=name)
    session.add(pin_type)
    session.commit()
    
    for field_name, field_type, is_required in fields:
        field = Field(pin_type_id=pin_type.id, name=field_name, field_type=field_type, is_required=is_required)
        session.add(field)
    
    session.commit()
    return pin_type

def add_pin(pin_type_name, latitude, longitude, field_values):
    pin_type = session.query(PinType).filter_by(name=pin_type_name).first()
    if not pin_type:
        raise ValueError(f"PinType '{pin_type_name}' does not exist.")
    
    pin = Pin(pin_type_id=pin_type.id, latitude=latitude, longitude=longitude)
    session.add(pin)
    session.commit()
    
    for field_name, value in field_values.items():
        field = session.query(Field).filter_by(pin_type_id=pin_type.id, name=field_name).first()
        if not field:
            raise ValueError(f"Field '{field_name}' does not exist for PinType '{pin_type_name}'.")
        
        field_value = FieldValue(pin_id=pin.id, field_id=field.id, value=value)
        session.add(field_value)
    
    session.commit()
    return pin

def get_pin_by_id(pin_id):
    pin = session.query(Pin).filter_by(id=pin_id).first()
    if not pin:
        raise ValueError(f"Pin with id '{pin_id}' does not exist.")
    
    pin_data = {
        "id": pin.id,
        "latitude": pin.latitude,
        "longitude": pin.longitude,
        "pin_type": pin.pin_type.name,
        "fields": {}
    }
    
    for field_value in pin.field_values:
        field = session.query(Field).filter_by(id=field_value.field_id).first()
        pin_data["fields"][field.name] = field_value.value
    
    return pin_data

def get_pins(pin_type_name):
    pin_type = session.query(PinType).filter_by(name=pin_type_name).first()
    if not pin_type:
        raise ValueError(f"PinType '{pin_type_name}' does not exist.")
    
    pins = session.query(Pin).filter_by(pin_type_id=pin_type.id).all()
    result = []
    for pin in pins:
        pin_data = {
            "id": pin.id,
            "latitude": pin.latitude,
            "longitude": pin.longitude,
            "fields": {}
        }
        for field_value in pin.field_values:
            field = session.query(Field).filter_by(id=field_value.field_id).first()
            pin_data["fields"][field.name] = field_value.value
        result.append(pin_data)
    
    return result

def get_all_pins():
    pins = session.query(Pin).all()
    result = []
    for pin in pins:
        pin_data = {
            "id": pin.id,
            "pin_type": pin.pin_type.name,
            "latitude": pin.latitude,
            "longitude": pin.longitude,
            "fields": {}
        }
        for field_value in pin.field_values:
            field = session.query(Field).filter_by(id=field_value.field_id).first()
            pin_data["fields"][field.name] = field_value.value
        result.append(pin_data)
    
    return result

def update_pin(pin_id, updated_field_values):
    pin = session.query(Pin).filter_by(id=pin_id).first()
    if not pin:
        raise ValueError(f"Pin with ID '{pin_id}' does not exist.")
    
    for field_name, new_value in updated_field_values.items():
        field = session.query(Field).filter_by(pin_type_id=pin.pin_type_id, name=field_name).first()
        if not field:
            raise ValueError(f"Field '{field_name}' does not exist for PinType ID '{pin.pin_type_id}'.")
        
        field_value = session.query(FieldValue).filter_by(pin_id=pin.id, field_id=field.id).first()
        if field_value:
            field_value.value = new_value
        else:
            field_value = FieldValue(pin_id=pin.id, field_id=field.id, value=new_value)
            session.add(field_value)
    
    session.commit()
    return pin

def delete_pin(pin_id):
    pin = session.query(Pin).filter_by(id=pin_id).first()
    if not pin:
        raise ValueError(f"Pin with ID '{pin_id}' does not exist.")
    
    session.delete(pin)
    session.commit()


def update_pin_type(pin_type_id, new_name=None, updated_fields=None):
    """
    Updates the name and fields of an existing PinType.

    :param pin_type_id: The ID of the PinType to update.
    :param new_name: The new name for the PinType (optional).
    :param updated_fields: A list of dictionaries containing the field updates.
                           Each dictionary should have 'id', 'name', 'field_type', and 'is_required'.
                           If 'id' is None, a new field is created.
                           If a field with 'id' is found, it's updated.
                           To delete a field, remove it from the list.
    :return: The updated PinType object.
    """
    pin_type = session.query(PinType).filter_by(id=pin_type_id).first()
    
    if not pin_type:
        raise ValueError(f"PinType with ID '{pin_type_id}' does not exist.")
    
    # Update the name if provided
    if new_name:
        pin_type.name = new_name
    
    # Update or add new fields
    existing_field_ids = {field.id for field in pin_type.fields}
    
    for field_data in updated_fields or []:
        field_id = field_data.get('id')
        field_name = field_data['name']
        field_type = field_data['field_type']
        is_required = field_data['is_required']
        
        if field_id:  # Update existing field
            if field_id in existing_field_ids:
                field = session.query(Field).filter_by(id=field_id).first()
                field.name = field_name
                field.field_type = field_type
                field.is_required = is_required
                existing_field_ids.remove(field_id)
            else:
                raise ValueError(f"Field with ID '{field_id}' does not exist for PinType '{pin_type.name}'.")
        else:  # Add new field
            new_field = Field(
                pin_type_id=pin_type.id,
                name=field_name,
                field_type=field_type,
                is_required=is_required
            )
            session.add(new_field)
    
    # Remove fields not in updated_fields
    for field_id in existing_field_ids:
        field_to_delete = session.query(Field).filter_by(id=field_id).first()
        session.delete(field_to_delete)
    
    session.commit()
    
    return pin_type


