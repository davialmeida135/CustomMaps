import flet as ft
import platform
class DotOverlay(ft.Container):
    def __init__(self):
        super().__init__(
            width=5,
            height=5,
            bgcolor=ft.colors.RED,
            border_radius=ft.border_radius.all(5),
            alignment=ft.alignment.center,
            visible=True, 
            ignore_interactions=True,# Make sure the dot is visible
            #absolute = True,
        )

def update_dot_position(page: ft.Page, dot_overlay):
    # Define the individual margins
    print("User agent> ",page.client_user_agent)
    if page.width > page.height:
        margin_top = 56
        margin_bottom = 165
        margin_left = 5
        margin_right = 0
    else:
        margin_top = 56
        margin_bottom = 204
        margin_left = 5
        margin_right = 0
    '''
    # Calculate the map's dimensions considering the margins
    map_width = page.width - (margin_left + margin_right)
    map_height = page.height - (margin_top + margin_bottom)
    
    # Calculate center position relative to the map
    dot_overlay.left = margin_left + (map_width - dot_overlay.width) / 2
    dot_overlay.top = margin_top + (map_height - dot_overlay.height) / 2
    '''
    map_width = page.width - (margin_left + margin_right)
    map_height = page.height - (margin_top + margin_bottom)

    # Calculate the map's center in pixels
    map_center_x = margin_left + (map_width / 2)
    map_center_y = margin_top + (map_height / 2)
    dot_overlay.margin = ft.margin.only(left=map_center_x,top=map_center_y)
    

    # Debugging the calculated positions
    #print(f"Map center position: left={dot_overlay.left}, top={dot_overlay.top}")
    page.update()
    
