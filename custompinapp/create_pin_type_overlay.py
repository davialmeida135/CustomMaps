"""
Module for creating and managing pin type overlays.

This module defines the CreatePinTypeOverlay class, which provides functionalities for creating, editing, and deleting pin types.

Classes:
    CreatePinTypeOverlay: A class for creating and managing pin type overlays.
"""
import flet as ft
from db.crud import create_pin_type
from flet_contrib.color_picker import ColorPicker
from map_overlay import update_dot_position, DotOverlay

class CreatePinTypeOverlay(ft.Column):
    """
    A class for creating and managing pin type overlays.

    Args:
        page (ft.Page): The main page object provided by Flet.
        on_pin_type_created (function): Callback function to be called when a pin type is created.
    """
    def __init__(self, page: ft.Page, on_pin_type_created):
        super().__init__()
        self.page = page
        self.pin_type_name_field = ft.TextField(label="Pin Type Name", expand=True)
        self.fields_list = ft.ListView(expand=True, spacing=5)
        self.add_field_button = ft.IconButton(icon=ft.icons.ADD, on_click=self.add_field)
        self.save_button = ft.ElevatedButton(text="Save", on_click=self.save_pin_type)
        self.cancel_button = ft.ElevatedButton(text="Cancel", on_click=self.cancel)
        self.on_pin_type_created = on_pin_type_created
        
        async def open_color_picker(e):
            self.page.dialog = d
            self.color_picker.color = self.color_icon.icon_color
            d.open = True
            await self.page.update()

        self.color_icon = ft.IconButton(icon="add_location", on_click=open_color_picker, icon_color="#36aedc")
        self.color_picker = ColorPicker(color=self.color_icon.icon_color, width=300)
        
        async def change_color(e):
            self.color_icon.icon_color = self.color_picker.color
            d.open = False
            await self.page.update()

        async def close_dialog(e):
            d.open = False
            await self.page.update()

        d = ft.AlertDialog(
            content=self.color_picker,
            actions=[
                ft.TextButton("OK", on_click=change_color),
                ft.TextButton("Cancel", on_click=close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            #on_dismiss=change_color,
        )
        
        self.controls = [
            ft.Text("Create New Pin Type", size=20, weight='bold'),
            ft.Row([
                self.pin_type_name_field,
                self.color_icon,]),
            ft.Text("Fields", size=16, weight='bold'),
            
            self.fields_list,
            self.add_field_button,
            
            ft.Row(controls=[self.save_button, self.cancel_button], alignment=ft.MainAxisAlignment.END)
        ]

    def add_field(self, e):
        """
        Add a new field to the pin type.

        Args:
            e: The event object.
        """
        field_name_field = ft.TextField(label="Field Name", expand=True)
        field_type_dropdown = ft.Dropdown(
            label="Field Type",
            options=[
                ft.dropdown.Option("string", "String"),
                ft.dropdown.Option("integer", "Integer"),
                ft.dropdown.Option("date", "Date")
            ],
            #autofocus=True,
            expand=True
        )
        is_required_checkbox = ft.Checkbox(label="Required", value=False)

        field_row = ft.Row(controls=[field_name_field, field_type_dropdown, is_required_checkbox])
        remove_button = ft.IconButton(icon=ft.icons.DELETE_OUTLINED, on_click=lambda e, field_row=field_row: self.remove_field(field_row))
        field_row.controls.append(remove_button)
        self.fields_list.controls.append(field_row)
        self.update()
        
    def remove_field(self, field_row):
        """
        Remove a field from the pin type.

        Args:
            field_row: The row object representing the field to be removed.
        """
        self.fields_list.controls.remove(field_row)
        self.update()
        
    def verify_field(self, field):
        """
        Verify the validity of a field.

        Args:
            field: The field object to be verified.
        """
        field.controls[0].error_text = None
        field.controls[1].error_text = None
        erro = False
        
        if not field.controls[0].value:
            field.controls[0].error_text = "Field Name is required."
            erro = True
        if not field.controls[1].value:
            field.controls[1].error_text = "Field Type is required"
            erro = True
        
        return erro

    def save_pin_type(self, e):
        """
        Save the pin type with the specified fields.

        Args:
            e: The event object.
        """
        erro = False
        # Limpa mensagens de erro
        self.pin_type_name_field.error_text = None

        #Verifica existência de pin com mesmo nome
        pin_type_name = self.pin_type_name_field.value
        if pin_type_name == "":
            self.pin_type_name_field.error_text = "Pin Type Name is required."
            self.page.update()
            erro = True
        
        #Adiciona campos ao tipo de pin
        fields = []
        for field_row in self.fields_list.controls:
            
            erro = self.verify_field(field_row) or erro
                
            field_name = field_row.controls[0].value
            field_type = field_row.controls[1].value
            is_required = field_row.controls[2].value
            fields.append((field_name, field_type, is_required))

        #Display dos erros
        if erro:
            print (erro)
            self.page.update()
            return
        
        #Criação do pin
        color = self.color_picker.color
        try:
            create_pin_type(pin_type_name, fields, color=color)
        except ValueError as e:
            self.pin_type_name_field.error_text = str(e)
            self.page.update()
            return
        
        # Call the callback function to update the dropdown
        self.on_pin_type_created()
    
        self.page.overlay.clear()
        dot_overlay = DotOverlay()
        self.page.overlay.append(dot_overlay)
        update_dot_position(self.page, dot_overlay)
        #self.page.update()

    def cancel(self, e):
        """
        Cancel the creation or editing of a pin type.

        Args:
            e: The event object.
        """
        self.page.overlay.clear()
        dot_overlay = DotOverlay()
        self.page.overlay.append(dot_overlay)
        update_dot_position(self.page, dot_overlay)    