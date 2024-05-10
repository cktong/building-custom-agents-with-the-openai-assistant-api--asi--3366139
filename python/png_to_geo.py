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

# Define mapping between pixel values and rainfall magnitude
# You'll need to define this mapping based on your data
rainfall_magnitude_mapping = {
    0: 0,  # Example: pixel value of 0 corresponds to rainfall magnitude of 0
    255: 10  # Example: pixel value of 255 corresponds to rainfall magnitude of 10
}

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
        magnitude = rainfall_magnitude_mapping.get(tuple(pixel_value), 0)  # Convert array to tuple
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
