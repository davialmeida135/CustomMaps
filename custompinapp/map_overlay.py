import flet as ft
import platform
class DotOverlay(ft.Container):
    """
    A class representing a dot overlay on the map.

    This class inherits from `ft.Container` and is used to create a small red dot
    that is centered on the map and ignores interactions.

    Attributes:
        width (int): The width of the dot.
        height (int): The height of the dot.
        bgcolor (str): The background color of the dot.
        border_radius (ft.BorderRadius): The border radius of the dot.
        alignment (ft.Alignment): The alignment of the dot.
        visible (bool): Whether the dot is visible.
        ignore_interactions (bool): Whether the dot ignores interactions.
    """
    def __init__(self):
        """
        Initialize a DotOverlay instance.

        This constructor sets the width, height, background color, border radius,
        alignment, visibility, and interaction properties of the dot.
        """
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
    """
    Update the position of the dot overlay on the map.

    This function calculates the center position of the map and updates the
    margin of the dot overlay to center it on the map.

    Args:
        page (ft.Page): The main page object provided by Flet.
        dot_overlay (DotOverlay): The dot overlay object to be positioned.
    """
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

    map_width = page.width - (margin_left + margin_right)
    map_height = page.height - (margin_top + margin_bottom)

    # Calculate the map's center in pixels
    map_center_x = margin_left + (map_width / 2)
    map_center_y = margin_top + (map_height / 2)
    dot_overlay.margin = ft.margin.only(left=map_center_x,top=map_center_y)
    

    # Debugging the calculated positions
    #print(f"Map center position: left={dot_overlay.left}, top={dot_overlay.top}")
    page.update()
    
