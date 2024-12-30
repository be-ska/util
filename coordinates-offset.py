import pandas as pd
import numpy as np

# Radius of the Earth in meters
EARTH_RADIUS = 6371000

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth using the Haversine formula.
    Input values are in degrees, and the result is in meters.
    """
    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    distance = EARTH_RADIUS * c  # Distance in meters
    return distance

def calculate_offset_and_angle(file_path):
    # Load the CSV file
    data = pd.read_csv(file_path)
    
    # Ensure required columns are present
    required_columns = ['loc', 'lat1', 'lon1', 'lat2', 'lon2']
    if not all(col in data.columns for col in required_columns):
        raise ValueError(f"CSV file must contain the columns: {', '.join(required_columns)}")
    
    # Calculate the distance (offset) in meters between the points using Haversine formula
    data['offset_m'] = haversine(data['lat1'], data['lon1'], data['lat2'], data['lon2'])
    
    # Convert the offset to centimeters
    data['offset_cm'] = data['offset_m'] * 100
    
    # Calculate the angle between the points (azimuth angle) in degrees
    lat1_r = np.radians(data['lat1'])
    lat2_r = np.radians(data['lat2'])
    lon_diff_r = np.radians(data['lon2'] - data['lon1'])
    
    x = np.sin(lon_diff_r) * np.cos(lat2_r)
    y = np.cos(lat1_r) * np.sin(lat2_r) - np.sin(lat1_r) * np.cos(lat2_r) * np.cos(lon_diff_r)
    data['angle_deg'] = (np.degrees(np.arctan2(x, y)) + 360) % 360  # Normalize to 0-360 degrees

    # Drop intermediate columns used for calculations
    data = data[['loc','offset_cm', 'angle_deg']]
    
    # Output the result
    print(data)

# Example usage
file_path = 'coordinates.csv'  # Replace with the path to your CSV file
calculate_offset_and_angle(file_path)
