from time import sleep
import flet as ft
import flet_core.map as map
import random
from marker_overlay import MarkerOverlay
import db.crud as pins_crud

from dot_overlay import DotOverlay, update_dot_position

def main(page: ft.Page):
    global last_center
    last_center = None
    class CustomMarker(map.Marker):

        def __init__(self, coordinates, id):
            super().__init__(coordinates=coordinates, content=None)
            self.content = ft.IconButton('add_location',on_click=self.handle_marker_click)
            self.coordinates = coordinates
            self.id = id

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
                    content=MarkerOverlay(page,self.coordinates,self.id),
                    padding=5,
                    #width=relative_width,
                    #height=relative_height,
                    bgcolor=ft.colors.LIGHT_BLUE_100,
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
        pins = pins_crud.get_all_pins()
        for pin in pins:
            coordinates = map.MapLatitudeLongitude(pin["latitude"], pin["longitude"])
            id = pin["id"]
            marker = CustomMarker(coordinates, id)
            marker_layer_ref.current.markers.append(marker)

        page.update()

    gl = ft.Geolocator()
    page.add(gl)

    def handle_permission_request(e):
        page.add(ft.Text(f"request_permission: {gl.request_permission()}"))  

    # Create dot overlay with initial position
    def update_dot_event(e):
        update_dot_position()

    def place_pin(type,lat,lng,fields, color = "ff0000"):
            # Add a new pin to the database
            pin = pins_crud.add_pin(type,lat,lng,fields)
            # Add a new marker to the map
            marker_layer_ref.current.markers.append(CustomMarker(map.MapLatitudeLongitude(pin.latitude, pin.longitude), pin.id,))
            page.update()

    def handle_event(e: map.MapEvent):
        print(
            f"{e.name} - Source: {e.source} - Center: {e.center} - Zoom: {e.zoom} - Rotation: {e.rotation}"
        )
        if e.source == map.MapEventSource.DRAG_END or e.source == map.MapEventSource.SCROLL_WHEEL:
            global last_center
            last_center = e.center
            

    def place_marker_at_center(e):
        if marker_layer_ref.current:
            if last_center is not None:        
                place_pin("Planta", last_center.latitude, last_center.longitude, {"Especie": "jajajajaja", "Data": "2002-03-03"})
                page.update()
            else:
                center = page_map.configuration.initial_center
                place_pin("Planta", center.latitude, center.longitude, {"Especie": "jajajajaja", "Data": "2002-03-03"})
                page.update()

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
                    flags=map.MapInteractiveFlag.ALL
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

    global marker_layer_ref, circle_layer_ref, page_map, map_pch
    page_map, marker_layer_ref, circle_layer_ref = build_map(5, 15, 9)


    def handle_find_myself(e):
        global marker_layer_ref, circle_layer_ref
        p = gl.get_current_position(ft.GeolocatorPositionAccuracy.BEST)
        if marker_layer_ref.current:
            marker_layer_ref.current.markers.append(
                map.Marker(
                    content=ft.Icon(
                        ft.icons.MY_LOCATION, color=ft.colors.BLUE
                    ),
                    coordinates=map.MapLatitudeLongitude(p.latitude, p.longitude),
                )
            )
            # Update the map's center to the current position
            print(f"Found Myself: ({p.latitude}, {p.longitude})")
            # Rebuild the map component
            map_pch.controls.clear()
            page_map, marker_layer_ref, circle_layer_ref = build_map(13, p.latitude, p.longitude)
            map_pch.controls.append(page_map)
            load_pins()
            page.update()

    map_pch = ft.Column(
        expand=1,
        controls=[page_map],
    )
    page.views.append(
        ft.View(
            "/",
            controls=[
                ft.OutlinedButton(
                    "request_permission",
                    on_click=handle_permission_request,
                ),
                ft.Text("Click anywhere to add a Marker, right-click to add a CircleMarker."),
                ft.ElevatedButton("Find Myself", on_click=handle_find_myself),
                map_pch,
                
            ],
            bottom_appbar=ft.BottomAppBar(
                        bgcolor=ft.colors.AMBER,
                        shape=ft.NotchShape.CIRCULAR,
                        content=ft.Row(
                            controls=[
                                ft.Container(expand=True),
                                ft.IconButton(icon=ft.icons.REMOVE_RED_EYE_OUTLINED, icon_color=ft.colors.WHITE,),
                                ft.IconButton(icon=ft.icons.LOGOUT, icon_color=ft.colors.WHITE, ),
                            ]
                        ),
                    ),
            floating_action_button = ft.FloatingActionButton(icon=ft.icons.ADD, 
                                                            bgcolor = ft.colors.AMBER,
                                                            on_click=place_marker_at_center
                                                            ),
            floating_action_button_location = ft.FloatingActionButtonLocation.CENTER_DOCKED,
            bgcolor = ft.colors.AMBER_600,

        )
        
    )

    dot_overlay = DotOverlay()
    # Add dot overlay to the page's overlay
    page.overlay.append(dot_overlay)
    update_dot_position(page, dot_overlay)

    page.on_resize = update_dot_event
    page.update()
    load_pins()
    

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    ft.app(target=main)