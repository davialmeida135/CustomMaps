import flet as ft
from db.crud import get_pin_by_id, update_pin, delete_pin
from map_overlay import DotOverlay, update_dot_position
import datetime

class Attribute(ft.Column):
    """
    A class representing an attribute of a pin.

    This class inherits from `ft.Column` and is used to display and edit attributes
    associated with a pin on the map.

    Attributes:
        attribute_name (str): The name of the attribute.
        attribute_value (str or dict): The value of the attribute. If a dictionary is provided,
                                       it should contain 'type' and 'value' keys.
        pin_id (int): The unique identifier of the pin.
        editable (bool): Whether the attribute is editable. Defaults to True.
        page (ft.Page): The main page object provided by Flet. Defaults to None.
        attribute_type (str): The type of the attribute if the value is a dictionary.
        icon (ft.Icon): The icon representing the attribute.
        display_field (ft.Text): The text field used to display the attribute value.
        edit_field (ft.TextField): The text field used to edit the attribute value.
        display_view (ft.Container): The container for displaying the attribute in view mode.
    """
    def __init__(self, attribute_name, attribute_value, pin_id,  editable = True, page: ft.Page = None):
        """
        Initialize an Attribute instance.

        Args:
            attribute_name (str): The name of the attribute.
            attribute_value (str or dict): The value of the attribute. If a dictionary is provided,
                                           it should contain 'type' and 'value' keys.
            pin_id (int): The unique identifier of the pin.
            editable (bool, optional): Whether the attribute is editable. Defaults to True.
            page (ft.Page, optional): The main page object provided by Flet. Defaults to None.
        """
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
        """
        Handle the click event for editing an attribute.

        This function is called when the edit button is clicked. It opens the date picker
        if the attribute type is 'date', or switches to the edit view for other attribute types.

        Args:
            e: The event object representing the click event.
        """
        def get_current_date():
            try:
                return datetime.datetime.strptime(self.display_field.value, '%Y-%m-%d')
            except:
                return datetime.datetime.now() 
        
        def handle_date_change(e):
            """
            Handle the change event for the date picker.

            This function is called when the date picker value changes. It updates the
            attribute value, display field, and the pin with the new date.

            Args:
                e: The event object containing the new date value.
            """
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
                    current_date=get_current_date(),
                    on_change=handle_date_change,  
                    )
                )
            elif self.attribute_type == 'integer':
                self.edit_field.value = self.display_field.value
                self.display_view.visible = False
                self.edit_view.visible = True
            else:
                self.edit_field.value = self.display_field.value
                self.display_view.visible = False
                self.edit_view.visible = True
                
        self.update()

    def save_clicked(self, e):
        """
        Handle the click event for saving an edited attribute.

        This function is called when the save button is clicked. It updates the attribute value,
        display field, and the pin with the new value.

        Args:
            e: The event object representing the click event.
        """
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
    """
    A class representing an overlay for a marker on the map.

    This class inherits from `ft.Column` and is used to display and manage
    the details and actions associated with a marker on the map.

    Attributes:
        page (ft.Page): The main page object provided by Flet.
        pin_id (int): The unique identifier of the pin.
        coordinates: The coordinates of the marker.
        expand (bool): Whether the overlay should expand to fill available space.
        pin_id_field (ft.Text): The text field displaying the pin ID.
        delete_button (ft.IconButton): The button to delete the marker.
        close_button (ft.IconButton): The button to close the overlay.
    """
    def __init__(self, page: ft.Page,coordinates ,id: int, load_pins):
        """
        Initialize a MarkerOverlay instance.

        Args:
            page (ft.Page): The main page object provided by Flet.
            coordinates: The coordinates of the marker.
            id (int): The unique identifier of the pin.
            load_pins (function): The function to load pins after deletion.
        """
        super().__init__()
        self.page=page
        self.pin_id = id
        self.coordinates = coordinates
        self.expand= True
        
        def clear_overlay(e):
            """
            Clear the overlay and reset the dot position.

            Args:
                e: The event object representing the click event.
            """
            self.page.overlay.clear()
            dot_overlay = DotOverlay()
            page.overlay.append(dot_overlay)
            update_dot_position(self.page, dot_overlay)
            #self.page.update()
        
        def delete_marker(e):
            """
            Delete the marker and reload pins.

            Args:
                e: The event object representing the click event.
            """
            try:
                print('delte pin called')
                delete_pin(self.pin_id)  # Call the function to delete the marker
                self.page.overlay.clear()
                print('load_pins called')
                load_pins()
                print('load_pins completed')
                dot_overlay = DotOverlay()
                page.overlay.append(dot_overlay)
                update_dot_position(self.page, dot_overlay)
                print("update_dot_position end")
            
            except Exception as ex:
                print(f"Error deleting marker: {ex}")

        pin_text = f'#{self.pin_id}'
        self.pin_id_field = ft.Text(value= pin_text, expand=True, color=ft.colors.BLACK, size=20, text_align=ft.TextAlign.JUSTIFY)
        self.delete_button = ft.IconButton(icon=ft.icons.DELETE_OUTLINED, on_click=delete_marker)
        self.close_button = ft.IconButton(icon=ft.icons.CLOSE, alignment=ft.alignment.center_right,on_click=clear_overlay)

        # Fetch pin details
        pin_details = get_pin_by_id(self.pin_id)
        pin_info_list = ft.ListView(expand=True,spacing=5)

        # Create a list view to display pin details
        def rebuild_pin_info():
            """
            Rebuild the pin information list view.

            This function clears the current controls in the pin information list view
            and appends the updated pin details.
            
            Returns:
                ft.ListView: The updated pin information list
            """
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
                        self.delete_button,
                        self.close_button,
                    ]
                ),
                pin_info_list,       
        ]

