from PIL import Image
import numpy as np
import json
import requests
import io
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# Define a class to map RGB colors to magnitudes automatically
class AutoColormap:
    def __init__(self, rgb_colors):
        self.rgb_colors = rgb_colors
        self.rgb_array = np.array(rgb_colors) / 255.0  # Normalize RGB values to [0, 1]
        self.num_colors = len(rgb_colors)

    def to_magnitude(self, rgb_value):
        # Find the index of the closest RGB color
        idx = np.argmin(np.linalg.norm(self.rgb_array - (rgb_value / 255.0), axis=1))
        # Return the corresponding magnitude, starting from 1
        return idx + 1

# Load extracted RGB colors from JSON file
with open("extracted_colors.json", "r") as file:
    extracted_colors = json.load(file)
extracted_colors.reverse()  # Reverse the colors if needed

# Convert RGB array to Matplotlib colormap
cmap = ListedColormap(np.array(extracted_colors) / 255.0)

month= "05"
day= "27"
year= "2024"
time= "1400"
# Fetch the rain data image from the URL
# url = "http://www.weather.gov.sg/files/rainarea/50km/v2/dpsri_70km_2024052514000000dBR.dpsri.png"
url = "http://www.weather.gov.sg/files/rainarea/50km/v2/dpsri_70km_"+year+month+day+time+"0000dBR.dpsri.png"
response = requests.get(url)
if response.status_code == 200:
    image_bytes = response.content
else:
    raise Exception(f"Failed to fetch data: {response.status_code}")

# Convert the image bytes to a PIL Image object
image = Image.open(io.BytesIO(image_bytes))

# Convert image to numpy array
rain_data = np.array(image)

# Define geographic boundaries and resolution
min_lat, max_lat = 1.47, 1.14
min_lon, max_lon = 103.55, 104.1
num_rows, num_cols = rain_data.shape[:2]

# Generate latitude and longitude arrays
latitudes = np.linspace(min_lat, max_lat, num_rows)
longitudes = np.linspace(min_lon, max_lon, num_cols)

# Initialize a list to hold GeoJSON features
features = []

# Initialize AutoColormap instance
auto_cmap = AutoColormap(extracted_colors)

# Initialize an array to hold magnitudes
magnitude = np.empty([rain_data.shape[0], rain_data.shape[1]])

# Iterate over each pixel in the rain data and map RGB values to rain magnitudes
for i in range(num_rows):
    for j in range(num_cols):
        rgb_value = rain_data[i, j][:3]
        if sum(rgb_value) == 0:
            magnitude[i, j] = np.NaN
        else:
            magnitude[i, j] = auto_cmap.to_magnitude(rgb_value)
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [longitudes[j], latitudes[i]]  # Note: GeoJSON coordinates are (lon, lat)
                },
                "properties": {
                    "magnitude": magnitude[i, j]
                }
            }
            features.append(feature)

# Create GeoJSON structure
geojson_data = {
    "type": "FeatureCollection",
    "features": features
}

# Save GeoJSON to file
output_file = "outputs/rainfall_magnitude_"+year+month+day+time+".geojson"
with open(output_file, "w") as f:
    json.dump(geojson_data, f, indent=2)
print("GeoJSON file saved:", output_file)

# Plot the colormap and display the scalar values on the colorbar
plt.figure(figsize=(10, 8))
plt.imshow(magnitude, cmap=cmap, aspect='auto')
plt.colorbar(label='Rain Magnitude')
plt.title('Rain Levels '+year+'/'+month+'/'+day+' Time:'+time)
plt.show()
plt.savefig('outputs/rain_magnitude_plot_'+year+month+day+time+'.png')
