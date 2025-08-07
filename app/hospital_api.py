import requests
import time

def get_address_from_coords(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        headers = {
            "User-Agent": "CataractFinder/1.0 (your_email@example.com)"
        }
        response = requests.get(url, headers=headers)
        data = response.json()
        return data.get("display_name", "Tidak diketahui")
    except:
        return "Tidak diketahui"

def get_nearby_hospitals(lat: float, lon: float, radius: int = 5000):
    url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    node["amenity"="hospital"](around:{radius},{lat},{lon});
    out;
    """
    response = requests.get(url, params={"data": query})
    data = response.json()

    hospitals = []
    elements = data.get("elements", [])[:10]  # ✅ Batasi hanya 5 rumah sakit

    for element in elements:
        name = element.get("tags", {}).get("name", "Unknown")
        h_lat = element.get("lat")
        h_lon = element.get("lon")

        address = get_address_from_coords(h_lat, h_lon)
        time.sleep(1)  # tetap disarankan agar tidak diblok

        hospitals.append({
            "name": name,
            "latitude": h_lat,
            "longitude": h_lon,
            "address": address
        })

    return hospitals

