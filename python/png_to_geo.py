from PIL import Image
import numpy as np
import json
import requests
import io

url = "http://www.weather.gov.sg/files/rainarea/50km/v2/dpsri_70km_2024051014150000dBR.dpsri.png"
response = requests.get(url)

if response.status_code == 200:
    image_bytes = response.content
else:
    print("Failed to fetch data:", response.status_code)

image_b = np.array(image_bytes)
# Convert the image bytes to a PIL Image object
image = Image.open(io.BytesIO(image_bytes))

# Convert image to numpy array
image_array = np.array(image)

# Define geographical extent (latitude and longitude ranges)
# You'll need to replace these with the actual coordinates
min_lat, max_lat = 1.5, 0.5
min_lon, max_lon = 103.5, 104.5

# Load the extracted colors from the JSON file
with open("extracted_colors.json", "r") as file:
    extracted_colors = json.load(file)

# Define a mapping from pixel values to rainfall magnitudes using the extracted colors
rainfall_magnitude_mapping = {}

# Assign magnitudes to colors based on their order in the extracted colors list
for i, color in enumerate(extracted_colors):
    # Define a magnitude range for each color
    # For simplicity, we'll use a range of (0, 5), (5, 10), (10, 15), and so on
    magnitude_range = (i * 5, (i + 1) * 5)
    # Add the color and its corresponding magnitude range to the mapping
    rainfall_magnitude_mapping[tuple(color)] = magnitude_range

print(rainfall_magnitude_mapping)
# Now, rainfall_magnitude_mapping contains the mapping from colors to rainfall magnitudes

# Convert pixel coordinates to geographical coordinates
# Assuming the image covers the entire geographical extent
num_rows, num_cols = image_array.shape[:2]
latitudes = np.linspace(min_lat, max_lat, num_rows)
longitudes = np.linspace(min_lon, max_lon, num_cols)

# Generate GeoJSON data
features = []
for i in range(num_rows):
    for j in range(num_cols):
        pixel_value = image_array[i, j]
        magnitude = rainfall_magnitude_mapping.get(tuple(pixel_value[:3]), 0)  # Consider only RGB values
        if sum(tuple(pixel_value[:3])) > 0:
           print(sum(pixel_value[:3]))
        # magnitude_sum = magnitude_sum + magnitude 
        latitude = latitudes[i]
        longitude = longitudes[j]
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [longitude, latitude]  # Note: GeoJSON coordinates are (lon, lat)
            },
            "properties": {
                "magnitude": magnitude
            }
        }
        features.append(feature)

# Create GeoJSON structure
geojson_data = {
    "type": "FeatureCollection",
    "features": features
}

# Save GeoJSON to file
output_file = "rainfall_magnitude.geojson"
with open(output_file, "w") as f:
    json.dump(geojson_data, f, indent=2)

print("GeoJSON file saved:", output_file)
