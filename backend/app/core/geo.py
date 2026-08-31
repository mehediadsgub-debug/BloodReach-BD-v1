"""
BloodReach BD — Geospatial & Distance Calculation Module
Provides Haversine distance calculations and coordinates for all 64 districts of Bangladesh.
"""

import math
from typing import Dict, Tuple, Optional

# Centroid latitude and longitude for all 64 districts of Bangladesh
DISTRICT_COORDINATES: Dict[str, Tuple[float, float]] = {
    # Dhaka Division
    "Dhaka": (23.8103, 90.4125),
    "Gazipur": (24.0023, 90.4267),
    "Narayanganj": (23.6238, 90.5000),
    "Narsingdi": (23.9193, 90.7176),
    "Manikganj": (23.8617, 90.0003),
    "Munshiganj": (23.5422, 90.5305),
    "Kishoreganj": (24.4260, 90.9821),
    "Tangail": (24.2513, 89.9167),
    "Faridpur": (23.6071, 89.8429),
    "Gopalganj": (23.0051, 89.8266),
    "Madaripur": (23.1641, 90.1897),
    "Rajbari": (23.7574, 89.6445),
    "Shariatpur": (23.2423, 90.4348),

    # Chattogram Division
    "Chattogram": (22.3569, 91.7832),
    "Cox's Bazar": (21.4272, 92.0058),
    "Cumilla": (23.4682, 91.1788),
    "Feni": (23.0186, 91.3966),
    "Brahmanbaria": (23.9571, 91.1119),
    "Chandpur": (23.2333, 90.6667),
    "Lakshmipur": (22.9425, 90.8412),
    "Noakhali": (22.8696, 91.0994),
    "Khagrachhari": (23.1193, 91.9847),
    "Rangamati": (22.7324, 92.2985),
    "Bandarban": (22.1953, 92.2184),

    # Rajshahi Division
    "Rajshahi": (24.3745, 88.6042),
    "Bogura": (24.8465, 89.3770),
    "Joypurhat": (25.1015, 89.0277),
    "Naogaon": (24.8103, 88.9416),
    "Natore": (24.4206, 89.0003),
    "Chapainawabganj": (24.5965, 88.2775),
    "Pabna": (24.0064, 89.2372),
    "Sirajganj": (24.4534, 89.7006),

    # Khulna Division
    "Khulna": (22.8456, 89.5403),
    "Bagerhat": (22.6516, 89.7859),
    "Satkhira": (22.7185, 89.0705),
    "Jashore": (23.1664, 89.2081),
    "Jhenaidah": (23.5450, 89.1726),
    "Magura": (23.4873, 89.4198),
    "Narail": (23.1725, 89.5127),
    "Kushtia": (23.9013, 89.1205),
    "Chuadanga": (23.6402, 88.8418),
    "Meherpur": (23.7622, 88.6318),

    # Barishal Division
    "Barishal": (22.7010, 90.3535),
    "Barguna": (22.1570, 90.1256),
    "Bhola": (22.6859, 90.6481),
    "Jhalokati": (22.6406, 90.1987),
    "Patuakhali": (22.3596, 90.3299),
    "Pirojpur": (22.5841, 89.9720),

    # Sylhet Division
    "Sylhet": (24.8949, 91.8687),
    "Habiganj": (24.3750, 91.4167),
    "Moulvibazar": (24.4829, 91.7774),
    "Sunamganj": (25.0658, 91.3950),

    # Rangpur Division
    "Rangpur": (25.7439, 89.2752),
    "Dinajpur": (25.6217, 88.6355),
    "Gaibandha": (25.3288, 89.5406),
    "Kurigram": (25.8054, 89.6362),
    "Lalmonirhat": (25.9923, 89.2847),
    "Nilphamari": (25.9310, 88.8560),
    "Panchagarh": (26.3411, 88.5541),
    "Thakurgaon": (26.0336, 88.4616),

    # Mymensingh Division
    "Mymensingh": (24.7471, 90.4203),
    "Jamalpur": (24.9375, 89.9377),
    "Netrokona": (24.8703, 90.7279),
    "Sherpur": (25.0204, 90.0152),
}


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on the Earth
    in kilometers using the Haversine formula.
    """
    R = 6371.0  # Earth radius in kilometers

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


def get_district_coordinates(district_name: Optional[str]) -> Optional[Tuple[float, float]]:
    """Retrieve latitude and longitude for a district name (case-insensitive)"""
    if not district_name:
        return None
    
    clean_name = district_name.strip()
    # Exact lookup
    if clean_name in DISTRICT_COORDINATES:
        return DISTRICT_COORDINATES[clean_name]
    
    # Case-insensitive lookup
    for name, coords in DISTRICT_COORDINATES.items():
        if name.lower() == clean_name.lower():
            return coords
            
    return None


def calculate_district_distance(district1: Optional[str], district2: Optional[str]) -> float:
    """
    Calculate distance in kilometers between two districts.
    Returns 0.0 if same district, 9999.0 if coordinates unavailable.
    """
    if not district1 or not district2:
        return 9999.0
    if district1.strip().lower() == district2.strip().lower():
        return 0.0

    c1 = get_district_coordinates(district1)
    c2 = get_district_coordinates(district2)
    if not c1 or not c2:
        return 9999.0

    return haversine_distance(c1[0], c1[1], c2[0], c2[1])
