import flet as ft
import flet_geolocator as ftg
import requests


API_URL = "http://127.0.0.1:5000"


def main(page: ft.Page):

    page.title = "GPS Location Tracker"
    page.padding = 20
    page.bgcolor = "#F2F5F9"
    page.theme_mode = ft.ThemeMode.LIGHT

    # --------------------------------------------------
    # GPS
    # --------------------------------------------------

    geolocator = ftg.Geolocator(
        location_settings=ftg.GeolocatorSettings(
            accuracy=ftg.GeolocatorPositionAccuracy.HIGH
        )
    )

    page.overlay.append(geolocator)

    # --------------------------------------------------
    # UI
    # --------------------------------------------------

    status_text = ft.Text(
        "Waiting...",
        color=ft.Colors.GREY_700
    )

    latitude_text = ft.Text("-")
    longitude_text = ft.Text("-")
    location_text = ft.Text("-")
    address_text = ft.Text("-")

    def info_row(title, value_control):

        return ft.Row(
            [
                ft.Text(
                    title,
                    weight=ft.FontWeight.BOLD,
                    width=100
                ),
                value_control
            ],
            spacing=10
        )

    # --------------------------------------------------
    # GET LOCATION
    # --------------------------------------------------

    async def get_location(e):

        get_button.disabled = True

        status_text.value = "Requesting GPS location..."
        page.update()

        try:

            # Request GPS permission
            permission = await geolocator.request_permission()

            if permission not in [
                ftg.GeolocatorPermissionStatus.ALWAYS,
                ftg.GeolocatorPermissionStatus.WHILE_IN_USE
            ]:

                status_text.value = "Location permission denied."

                get_button.disabled = False
                page.update()

                return

            status_text.value = "Getting live GPS location..."
            page.update()

            # Get current GPS position
            position = await geolocator.get_current_position(
                desired_accuracy=ftg.GeolocatorPositionAccuracy.HIGH
            )

            latitude = position.latitude
            longitude = position.longitude
            accuracy = position.accuracy

            # Display GPS immediately
            latitude_text.value = f"{latitude:.8f}"
            longitude_text.value = f"{longitude:.8f}"

            status_text.value = "Sending location to server..."
            page.update()

            # --------------------------------------------------
            # SEND GPS TO FLASK
            # --------------------------------------------------

            response = requests.post(
                f"{API_URL}/api/location",
                json={
                    "latitude": latitude,
                    "longitude": longitude,
                    "accuracy": accuracy
                },
                timeout=15
            )

            data = response.json()

            if data.get("success"):

                location_text.value = data.get(
                    "location_name",
                    "Unknown location"
                )

                address_text.value = data.get(
                    "display_name",
                    "Unknown address"
                )

                status_text.value = (
                    "Location found successfully"
                )

            else:

                status_text.value = data.get(
                    "message",
                    "Location request failed"
                )

        except requests.exceptions.ConnectionError:

            status_text.value = (
                "Cannot connect to Flask server."
            )

        except requests.exceptions.Timeout:

            status_text.value = (
                "Flask server request timed out."
            )

        except Exception as error:

            print("GPS ERROR:", error)

            status_text.value = (
                f"GPS error: {error}"
            )

        finally:

            get_button.disabled = False
            page.update()

    # --------------------------------------------------
    # BUTTON
    # --------------------------------------------------

    get_button = ft.Button(
        "Get My Location",
        icon=ft.Icons.LOCATION_ON,
        on_click=get_location,
        width=450,
        height=55
    )

    # --------------------------------------------------
    # RESULT BOX
    # --------------------------------------------------

    result_box = ft.Container(
        content=ft.Column(
            [
                info_row(
                    "Status:",
                    status_text
                ),

                info_row(
                    "Latitude:",
                    latitude_text
                ),

                info_row(
                    "Longitude:",
                    longitude_text
                ),

                info_row(
                    "Location:",
                    location_text
                ),

                info_row(
                    "Address:",
                    address_text
                )
            ],
            spacing=15
        ),

        padding=20,
        bgcolor="#F5F5F5",
        border_radius=12,

        margin=ft.Margin(
            top=20,
            left=0,
            right=0,
            bottom=0
        )
    )

    # --------------------------------------------------
    # MAIN CONTAINER
    # --------------------------------------------------

    container = ft.Container(

        content=ft.Column(
            [
                ft.Text(
                    "📍 GPS Location",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),

                ft.Container(
                    content=get_button,
                    margin=ft.Margin(
                        top=15,
                        left=0,
                        right=0,
                        bottom=0
                    )
                ),

                result_box
            ],

            horizontal_alignment=(
                ft.CrossAxisAlignment.CENTER
            ),

            spacing=10
        ),

        width=500,
        padding=25,
        bgcolor=ft.Colors.WHITE,
        border_radius=15,

        shadow=ft.BoxShadow(
            blur_radius=20,
            spread_radius=1,
            offset=ft.Offset(0, 5)
        )
    )

    # --------------------------------------------------
    # ADD TO PAGE
    # --------------------------------------------------

    page.add(
        ft.Row(
            [container],
            alignment=ft.MainAxisAlignment.CENTER
        )
    )


# --------------------------------------------------
# START FLET
# --------------------------------------------------

ft.run(main)