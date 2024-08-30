import flet as ft
from db.crud import get_pin_by_id, update_pin
from dot_overlay import DotOverlay, update_dot_position
import datetime

class Attribute(ft.Column):
    def __init__(self, attribute_name, attribute_value, pin_id,  editable = True, page: ft.Page = None):
        super().__init__()
        self.attribute_name = attribute_name
        self.attribute_value = attribute_value
        self.pin_id = pin_id
        self.editable = editable
        self.page = page
        
        if type(self.attribute_value) == dict:
            self.attribute_type = self.attribute_value['type']
            self.attribute_value = self.attribute_value['value']
        
        
        self.icon = ft.Icon(ft.icons.PIN_DROP_ROUNDED)
        
        self.display_field = ft.Text(value=self.attribute_value, color=ft.colors.GREY_700, weight="bold")
        self.edit_field = ft.TextField(expand=1)

        self.display_view = ft.Container(
                padding= 0,
                border_radius= 15,
                #bgcolor=ft.colors.RED,
                border = ft.border.all(2, ft.colors.GREY),
                content=ft.Row(
                [
                    ft.Container(
                        ft.Icon(ft.icons.ADD_LOCATION, size=30, color=ft.colors.GREY,),
                        margin=ft.margin.only(left=10,right=20)
                    ),
                    
                    ft.Container(
                        content=ft.Text(self.attribute_name, color=ft.colors.GREY_500, weight="bold", size=14, expand=True),
                        #bgcolor=ft.colors.ORANGE_300,
                        alignment=ft.alignment.center_left,
                        #width=50,
                        #expand=True,
                        margin=ft.margin.only(left=10,right=20)
                        ,
                    ),
                    ft.Container(
                        bgcolor=ft.colors.GREY,
                        #expand=True,
                        width=2,
                        height=50,
                        #margin= ft.margin.only(left=20,right=5),
                    ),
                    #ft.VerticalDivider(),
                    ft.Container(
                        content=self.display_field,
                        #bgcolor=ft.colors.BROWN_400,
                        alignment=ft.alignment.center,
                        expand=True,
                    ),
                    
                ],
                spacing=1,
                
                expand=True,
            ),
            )
        
        if editable:
            self.display_view.content.controls.append(
                ft.Container(
                        content=ft.IconButton(
                            icon=ft.icons.CREATE_OUTLINED,
                            tooltip="Edit",
                            on_click=self.edit_clicked,
                            ),
                    )
            )

        self.edit_view = ft.Container(
                visible=False,
                padding= 0,
                border_radius= 15,
                #bgcolor=ft.colors.RED,
                border = ft.border.all(2, ft.colors.GREY),
                content=ft.Row(
                [
                    ft.Container(
                        ft.Icon(ft.icons.ADD_LOCATION, size=30, color=ft.colors.GREY,),
                        margin=ft.margin.only(left=10,right=20)
                    ),
                    
                    ft.Container(
                        content=ft.Text(self.attribute_name, color=ft.colors.GREY_500, weight="bold", size=14, expand=True),
                        #bgcolor=ft.colors.ORANGE_300,
                        alignment=ft.alignment.center_left,
                        #width=50,
                        #expand=True,
                        margin=ft.margin.only(left=10,right=20)
                        ,
                    ),
                    ft.Container(
                        bgcolor=ft.colors.GREY,
                        #expand=True,
                        width=2,
                        height=50,
                        #margin= ft.margin.only(left=20,right=5),
                    ),
                    #ft.VerticalDivider(),
                    ft.Container(
                        content=self.edit_field,
                        #bgcolor=ft.colors.BROWN_400,
                        alignment=ft.alignment.center,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.IconButton(
                            icon=ft.icons.CLOSE_OUTLINED,
                            tooltip="Close",
                            on_click=self.close_clicked,
                            ),
                    ),
                    ft.IconButton(
                        icon=ft.icons.DONE_OUTLINE_OUTLINED,
                        icon_color=ft.colors.GREEN,
                        tooltip="Update",
                        on_click=self.save_clicked,
                    ),
                    
                ],
                spacing=1,
                
                expand=True,
            ),
            )
        
        self.controls = [self.display_view, self.edit_view]
        
    

    def edit_clicked(self, e):
        
        def handle_date_change(e):
            date = str(e.control.value).split(' ')[0]
            
            self.attribute_value = date
            self.display_field.value = date
            date = {}
            date[self.attribute_name] = self.attribute_value
            update_pin(self.pin_id, date)

            print(date)
            self.update()
            
        if self.editable:
            if self.attribute_type == 'date':
                          
                self.page.open(
                    ft.DatePicker(
                    current_date=datetime.datetime.strptime(self.display_field.value, '%Y-%m-%d'),
                    on_change=handle_date_change,  
                    )
                )
                
            elif self.attribute_type == 'integer':
                self.edit_field = ft.TextField(value = self.attribute_value)
                self.display_view.visible = False
                self.edit_view.visible = True
            else:
                self.edit_field.value = self.display_field.value
                self.display_view.visible = False
                self.edit_view.visible = True
                
        self.update()

    def save_clicked(self, e):
        updated_field_values = {}
        
        if self.editable:
            if self.attribute_type == 'integer':
                self.attribute_value = self.edit_field.value      
                print('saving integer field ' + self.attribute_value)
                self.display_field.value = self.edit_field.value      
                updated_field_values[self.attribute_name] = self.edit_field.value

            else:
                self.attribute_value = self.edit_field.value
                print('saving string field ' + self.attribute_value)
                self.display_field.value = self.edit_field.value             
                updated_field_values[self.attribute_name] = self.edit_field.value
                
        update_pin(self.pin_id, updated_field_values)

        #update_pin(self.pin_id, updated_field_values)
        self.display_view.visible = True
        self.edit_view.visible = False
        self.update()
        
    def close_clicked(self, e):
        self.display_view.visible = True
        self.edit_view.visible = False
        self.update()


class MarkerOverlay(ft.Column):
    def __init__(self, page: ft.Page,coordinates ,id: int):
        super().__init__()
        self.page=page
        self.pin_id = id
        self.coordinates = coordinates
        self.expand= True
        print(self.page)
        
        def clear_overlay(e):
            print(self.page)
            self.page.overlay.clear()

            dot_overlay = DotOverlay()

            page.overlay.append(dot_overlay)
            update_dot_position(self.page, dot_overlay)
            #self.page.update()


        pin_text = f'#{self.pin_id}'
        self.pin_id_field = ft.Text(value= pin_text, expand=True, color=ft.colors.BLACK, size=20, text_align=ft.TextAlign.JUSTIFY)
        self.close_button = ft.IconButton(icon=ft.icons.CLOSE, icon_color=ft.colors.WHITE, alignment=ft.alignment.center_right,on_click=clear_overlay)
        
        # Fetch pin details
        pin_details = get_pin_by_id(self.pin_id)
        pin_info_list = ft.ListView(expand=True,spacing=5)

        # Create a list view to display pin details
        def rebuild_pin_info():
            pin_info_list.controls.clear()
            
            pin_info_list.controls.append(Attribute('Pin Type',pin_details['pin_type'],self.pin_id, editable=False))
            position_text = f"{pin_details['latitude']}, {pin_details['longitude']}"
            pin_info_list.controls.append(Attribute('Position',position_text,self.pin_id,editable=False))
            for field_name, value in pin_details['fields'].items():
                pin_info_list.controls.append(Attribute(field_name,dict(value),self.pin_id,editable=True, page = self.page))
                print(value)
            return pin_info_list

        rebuild_pin_info()
        
        self.controls = [
                ft.Row(
                    controls=[
                        self.pin_id_field,
                        self.close_button,
                    ]
                ),
                pin_info_list,       
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