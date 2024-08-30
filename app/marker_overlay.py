import flet as ft
from db.crud import get_pin_by_id
from dot_overlay import DotOverlay, update_dot_position

class MarkerOverlay(ft.Column):
    def __init__(self, page: ft.Page,coordinates ,id: int):
        super().__init__()
        self.page=page
        self.pin_id = id
        self.coordinates = coordinates

        print(self.page)
        

        if self.page.width > self.page.height:
            self.margem = ft.margin.symmetric(horizontal=self.page.width/4, vertical=self.page.height/6)
            self.relative_width = self.page.width/2
            self.relative_height = self.page.height/2
        else:
            self.margem = ft.margin.symmetric(horizontal=self.page.width/10, vertical=self.page.height/6)
            self.relative_width = self.page.width/1.2
            self.relative_height = self.page.height/2

        def clear_overlay(e):
            print(self.page)
            self.page.overlay.clear()

            dot_overlay = DotOverlay()

            page.overlay.append(dot_overlay)
            update_dot_position(self.page, dot_overlay)
            #self.page.update()



        self.pin_id_field = ft.TextField(read_only=True,value= self.pin_id,filled=True ,bgcolor = ft.colors.WHITE,expand=True, color=ft.colors.BLACK )
        self.close_button = ft.IconButton(icon=ft.icons.CLOSE, icon_color=ft.colors.WHITE, alignment=ft.alignment.center_right,on_click=clear_overlay)
        
        

        self.controls = [
                ft.Row(
                    controls=[
                        self.pin_id_field,
                        self.close_button,
                    ]
                ),       
        ]

'''import flet as ft

def build_form_display(form_template):
    display_rows = []

    # Add permanent fields to display
    for field in form_template.permanent_fields:
        value = field.get_value()
        display_rows.append(ft.Text(f"{field.name}: {value}"))

    # Add custom fields to display
    for field in form_template.custom_fields:
        value = field.get_value()
        display_rows.append(ft.Text(f"{field.name}: {value}"))

    return display_rows

# Example usage
if __name__ == "__main__":
    form_template = FormTemplate("Example Form")
    form_template.permanent_fields.append(PermanentField("id", "12345"))
    form_template.permanent_fields.append(PermanentField("name", "John Doe"))
    form_template.custom_fields.append(StringField("email"))
    form_template.custom_fields.append(NumberField("age"))

    # Fill the form with example values
    filled_form = form_template.fill_form()

    # Build the form display
    display_rows = build_form_display(form_template)

    # Create a Flet page to display the form
    def main(page: ft.Page):
        page.add(ft.ListView(controls=display_rows))

    ft.app(target=main)'''