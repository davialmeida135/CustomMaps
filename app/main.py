from time import sleep
import flet as ft
import flet_core.map as map
import random
from create_pin_type_overlay import CreatePinTypeOverlay
from marker_overlay import MarkerOverlay
import db.crud as pins_crud
from map_overlay import DotOverlay, update_dot_position
import config

async def main(page: ft.Page):
    global last_center
    last_center = None
    dot_overlay = DotOverlay()
    global selected_pin_type
    pin_types = pins_crud.get_all_pin_types()
    selected_pin_type = pin_types[0]
    
    
    class CustomMarker(map.Marker):
        def __init__(self, coordinates, id, color):
            super().__init__(coordinates=coordinates, content=None)
            self.color = color
            self.coordinates = coordinates
            self.id = id
            self.content = ft.IconButton('add_location',on_click=self.handle_marker_click, icon_color=self.color)
            
        def handle_marker_click(self, e):
            if page.width > page.height:
                margem = ft.margin.symmetric(horizontal=page.width/4, vertical=page.height/6)
                relative_width = page.width/2
                relative_height = page.height/3
            else:
                margem = ft.margin.symmetric(horizontal=page.width/10, vertical=page.height/6)
                relative_width = page.width/1.2
                relative_height = page.height/2

            page.overlay.clear()
            page.overlay.append(
                ft.Container(
                    content=MarkerOverlay(page,self.coordinates,self.id, load_pins=load_pins),
                    padding=5,
                    #width=relative_width,
                    #height=relative_height,
                    bgcolor=config.SECONDARY_COLOR,
                    alignment=ft.alignment.center,
                    border_radius=ft.border_radius.all(10),
                    margin=margem,
                    shadow=ft.BoxShadow(
                        spread_radius=0.5,
                        blur_radius=5,
                        color=ft.colors.BLACK,
                        offset=ft.Offset(0, 0),
                        blur_style=ft.ShadowBlurStyle.NORMAL,
                    ),
                )
            )

            page.update()
  

        def __str__(self):
            return f"CustomMarker({self.coordinates})"
        
    def load_pins():
        print("Loading pins...")
        marker_layer_ref.current.markers.clear()
        pins = pins_crud.get_all_pins()
        for pin in pins:
            coordinates = map.MapLatitudeLongitude(pin["latitude"], pin["longitude"])
            id = pin["id"]
            marker = CustomMarker(coordinates, id, pin['color'])
            marker_layer_ref.current.markers.append(marker)

        print("Loaded pins!")
        page.update()
        
    global gl
    gl = ft.Geolocator()
    page.add(gl)
    
    def handle_permission_request(e):
        global gl
        page.add(ft.Text(f"request_permission: {gl.request_permission()}")) 

    # Create dot overlay with initial position
    def update_dot_event(e):
        print("update dot position")
        update_dot_position(page, dot_overlay)

    def place_pin(type,lat,lng,fields, color = "ff0000"):
            # Add a new pin to the database
            pin = pins_crud.add_pin(type,lat,lng,fields)
            # Add a new marker to the map
            marker_layer_ref.current.markers.append(CustomMarker(map.MapLatitudeLongitude(pin.latitude, pin.longitude), pin.id,pin.pin_type.color))
            page.update()
            
    def generate_empty_fields():
        global selected_pin_type
        fields = pins_crud.get_pin_type_by_name(selected_pin_type['name'])['fields']
        empty_fields = {}
        for field in fields:
            empty_fields[field['name']] = ""
        return empty_fields
        
    def place_marker_at_center(e):
        global selected_pin_type
        fields = generate_empty_fields()
        
        if marker_layer_ref.current:
            if last_center is not None:        
                place_pin(selected_pin_type['name'], last_center.latitude, last_center.longitude, fields )
                page.update()
            else:
                center = page_map.configuration.initial_center
                place_pin(selected_pin_type['name'], center.latitude, center.longitude,{})
                page.update()
                
    def handle_event(e: map.MapEvent):
            print(
                f"{e.name} - Source: {e.source} - Center: {e.center} - Zoom: {e.zoom} - Rotation: {e.rotation}"
            )
            if e.source == map.MapEventSource.DRAG_END or e.source == map.MapEventSource.SCROLL_WHEEL:
                global last_center
                last_center = e.center
                
    def build_map(zoom, latitude, longitude):
        marker_layer_ref = ft.Ref[map.MarkerLayer]()
        circle_layer_ref = ft.Ref[map.CircleLayer]()
        map_ref = ft.Ref[map.Map]()

        page_map = map.Map(
            ref=map_ref,
            expand=True,
            configuration=map.MapConfiguration(
                initial_center=map.MapLatitudeLongitude(latitude, longitude),
                initial_zoom=zoom,
                interaction_configuration=map.MapInteractionConfiguration(
                flags=map.MapInteractiveFlag.DRAG | map.MapInteractiveFlag.PINCH_ZOOM
                ),
                on_init=lambda e: print(f"Initialized Map"),
                #on_tap=handle_tap,
                #on_secondary_tap=handle_tap,
                #on_long_press=handle_tap,
                on_event=handle_event,
            ),
            layers=[
                map.TileLayer(
                    url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                    on_image_error=lambda e: print("TileLayer Error"),
                ),
                map.RichAttribution(
                    attributions=[
                        map.TextSourceAttribution(
                            text="OpenStreetMap Contributors",
                            on_click=lambda e: e.page.launch_url(
                                "https://openstreetmap.org/copyright"
                            ),
                        ),
                        map.TextSourceAttribution(
                            text="Flet",
                            on_click=lambda e: e.page.launch_url("https://flet.dev"),
                        ),
                    ]
                ),
                map.SimpleAttribution(
                    text="Flet",
                    alignment=ft.alignment.top_right,
                    on_click=lambda e: print("Clicked SimpleAttribution"),
                ),
                map.MarkerLayer(
                    ref=marker_layer_ref,
                    markers=[
                        # Add initial markers if any
                    ],
                ),
                map.CircleLayer(
                    ref=circle_layer_ref,
                    circles=[
                        # Add initial circles if any
                    ],
                ),
            ],
        )
        return page_map, marker_layer_ref, circle_layer_ref

    
    
    def build_pin_type_menu_items():
        pin_types = pins_crud.get_all_pin_types()
        print("================================================")
        #print(pin_types)
        menu_items = []
        for pin_type in pin_types:
            menu_items.append(
                ft.PopupMenuItem(
                    content=ft.Row([ft.Icon(name=pin_type['style'], color=pin_type['color']),
                                   ft.Text(value= pin_type['name'])]),
                    on_click=lambda e, pin_type=pin_type: handle_pin_type_selection(pin_type)
                )
            )
        
        return menu_items
     
    def build_pin_type_popup_button():
        global selected_pin_type
        pin_types = pins_crud.get_all_pin_types()
        if pin_types:
            popup_button = ft.PopupMenuButton(
                content=ft.Row([ft.Icon(name=selected_pin_type['style'], color=selected_pin_type['color']),
                                   ft.Text(value= selected_pin_type['name'],color=config.ICON_COLOR,weight=ft.FontWeight.BOLD)]),

                items=build_pin_type_menu_items()
            )
            return popup_button
        return None
    
    def update_pin_type_dropdown():
        global pin_type_dropdown
        pin_type_dropdown.content.controls.clear()
        pin_type_dropdown.content.controls.append(build_pin_type_popup_button())
        page.update()
        
    def handle_pin_type_selection(pin_type):
        #print(pin_type)
        global selected_pin_type
        
        selected_pin_type = pin_type
        print(f"Selected pin type: {selected_pin_type}")
        update_pin_type_dropdown()

    global marker_layer_ref, circle_layer_ref, page_map, map_pch
    page_map, marker_layer_ref, circle_layer_ref = build_map(5, 15, 9)    
    
    def handle_find_myself(e):
        global marker_layer_ref, circle_layer_ref,gl
        try:
            p = gl.get_current_position(ft.GeolocatorPositionAccuracy.BEST_FOR_NAVIGATION)
            if marker_layer_ref.current:
                # Update the map's center to the current position
                print(f"Found Myself: ({p.latitude}, {p.longitude})")
                # Rebuild the map component
                map_pch.controls.clear()
                page_map, marker_layer_ref, circle_layer_ref = build_map(16, p.latitude, p.longitude)
                map_pch.controls.append(page_map)
                page.update()
                load_pins()
                page.update()
        except Exception as e:
            print(f"Error: {e}")
            page.update()
              
    def show_create_pin_type_overlay(e):
        page.overlay.clear()
        page.overlay.append(
            ft.Container(
                content=CreatePinTypeOverlay(page, on_pin_type_created=update_pin_type_dropdown),
                padding=5,
                width=page.width,
                height=page.height,
                bgcolor=config.SECONDARY_COLOR,
                alignment=ft.alignment.center,
                border_radius=ft.border_radius.all(10),
                margin=ft.margin.symmetric(horizontal=10, vertical=30),
                #border=ft.border.all(width=2, color=config.SECONDARY_DARK_COLOR),
                shadow=ft.BoxShadow(
                    spread_radius=0.5,
                    blur_radius=5,
                    color=ft.colors.BLACK,
                    offset=ft.Offset(0, 0),
                    blur_style=ft.ShadowBlurStyle.NORMAL,
                ),
            )
        )
        page.update()

    map_pch = ft.Column(
        expand=1,
        controls=[page_map],
    )
    
    global pin_type_dropdown
    
    pin_type_dropdown = ft.Container(ft.Row())
    pin_type_dropdown.content.controls.append(build_pin_type_popup_button())
    update_pin_type_dropdown()
    
    page.views.append(
        ft.View(
            padding=0,
            route="/",
            controls=[
                map_pch,      
            ],
            appbar=ft.AppBar(
                #leading=ft.IconButton(icon=ft.icons.MENU, on_click=handle_permission_request),
                bgcolor=config.MAIN_COLOR,
                actions=[
                    ft.Row(
                        [
                        
                        ft.IconButton(icon=ft.icons.MESSAGE, on_click=handle_permission_request),
                        ft.IconButton(icon=ft.icons.LOCATION_SEARCHING, on_click=handle_find_myself)
                        ]
                ,),
                ],
            ),
            bottom_appbar=ft.BottomAppBar(
                        bgcolor=config.MAIN_COLOR,
                        shape=ft.NotchShape.CIRCULAR,
                        content=ft.Row(
                            controls=[
                                ft.IconButton(icon=ft.icons.ADD_CIRCLE_OUTLINE_OUTLINED, icon_color=config.ICON_COLOR, on_click=show_create_pin_type_overlay),
                                pin_type_dropdown,
                                
                            ]
                        ),
                    ),
            floating_action_button = ft.FloatingActionButton(icon=ft.icons.ADD, 
                                                            bgcolor = config.DARK_COLOR,
                                                            on_click=place_marker_at_center
                                                            ),
            floating_action_button_location = ft.FloatingActionButtonLocation.CENTER_DOCKED,
            bgcolor = config.SECONDARY_COLOR,

        )
        
    )

    # Add dot overlay to the page's overlay
    page.overlay.append(dot_overlay)
    update_dot_position(page, dot_overlay)

    page.on_resize = update_dot_event
    load_pins()
    page.update()

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    ft.app(target=main)