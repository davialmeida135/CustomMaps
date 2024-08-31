import flet as ft
from db.crud import create_pin_type
from flet_contrib.color_picker import ColorPicker

class CreatePinTypeOverlay(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.pin_type_name_field = ft.TextField(label="Pin Type Name", expand=True)
        self.fields_list = ft.ListView(expand=True, spacing=5)
        self.add_field_button = ft.IconButton(icon=ft.icons.ADD, on_click=self.add_field)
        self.save_button = ft.ElevatedButton(text="Save", on_click=self.save_pin_type)
        self.cancel_button = ft.ElevatedButton(text="Cancel", on_click=self.cancel)
        
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
            self.pin_type_name_field,
            self.color_icon,
            ft.Text("Fields", size=16, weight='bold'),
            self.fields_list,
            self.add_field_button,
            ft.Row(controls=[self.save_button, self.cancel_button], alignment=ft.MainAxisAlignment.END)
        ]

    def add_field(self, e):
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
        self.fields_list.controls.remove(field_row)
        self.update()
        
    def verify_field(self, field):
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
        erro = False
        # Limpa mensagens de erro
        self.pin_type_name_field.error_text = None

        #Verifica existência de pin com mesmo nome
        pin_type_name = self.pin_type_name_field.value
        if pin_type_name == "":
            self.pin_type_name_field.error_text = "Pin Type Name is required."
            self.page.update()
            erro = True
        
        
        fields = []
        for field_row in self.fields_list.controls:
            
            erro = self.verify_field(field_row) or erro
                
            field_name = field_row.controls[0].value
            field_type = field_row.controls[1].value
            is_required = field_row.controls[2].value
            fields.append((field_name, field_type, is_required))

        if erro:
            print (erro)
            self.page.update()
            return
        color = self.color_picker.color
        try:
            create_pin_type(pin_type_name, fields, color=color)
        except ValueError as e:
            self.pin_type_name_field.error_text = str(e)
            self.page.update()
            return
        
        self.page.overlay.clear()
        self.page.update()

    def cancel(self, e):
        self.page.overlay.clear()
        self.page.update()
        

'''def main(page: ft.Page):
    page.title = "ToDo App"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE

    # create app control and add it to the page
    page.add(CreatePinTypeOverlay(page))


ft.app(main)'''