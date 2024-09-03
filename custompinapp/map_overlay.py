import flet as ft
import db.crud as pins_crud
class DotOverlay(ft.Container):
    def __init__(self):
        super().__init__(
            width=5,
            height=5,
            bgcolor=ft.colors.RED,
            border_radius=ft.border_radius.all(5),
            alignment=ft.alignment.center,
            visible=True, 
            ignore_interactions=False,# Make sure the dot is visible
        )

def update_dot_position(page, dot_overlay):
    # Define the individual margins
    margin_top = 0
    margin_bottom = 110
    margin_left = 20
    margin_right = 10
    # Calculate the map's dimensions considering the margins
    map_width = page.width - (margin_left + margin_right)
    map_height = page.height - (margin_top + margin_bottom)
    
    # Calculate center position relative to the map
    dot_overlay.left = margin_left + (map_width - dot_overlay.width) / 2
    dot_overlay.top = margin_top + (map_height - dot_overlay.height) / 2

    # Debugging the calculated positions
    print(f"Map center position: left={dot_overlay.left}, top={dot_overlay.top}")
    page.update()
    
