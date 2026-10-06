from flask import Flask, render_template, jsonify, request
import requests

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.py")


@app.route("/api/location", methods=["POST"])
def get_location():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No location data received"
        }), 400

    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if latitude is None or longitude is None:
        return jsonify({
            "success": False,
            "message": "Latitude and longitude are required"
        }), 400

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Invalid coordinates"
        }), 400

    # Reverse geocoding
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "lat": latitude,
                "lon": longitude,
                "format": "json",
                "zoom": 18
            },
            headers={
                "User-Agent": "SimpleGPSLocationTracker/1.0"
            },
            timeout=10
        )

        response.raise_for_status()

        geo_data = response.json()

        address = geo_data.get("address", {})

        location_name = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("municipality")
            or "Unknown location"
        )

        return jsonify({
            "success": True,
            "latitude": latitude,
            "longitude": longitude,
            "location_name": location_name,
            "display_name": geo_data.get(
                "display_name",
                "Unknown address"
            )
        })

    except requests.RequestException:

        return jsonify({
            "success": True,
            "latitude": latitude,
            "longitude": longitude,
            "location_name": "Location name unavailable",
            "display_name": "Reverse geocoding failed"
        })


if __name__ == "__main__":
    app.run(debug=True)