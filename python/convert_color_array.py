from PIL import Image
import numpy as np
import json
import requests
import io
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, Normalize
from matplotlib.cm import ScalarMappable

class AutoColormap:
    def __init__(self, rgb_colors):
        self.rgb_colors = rgb_colors
        self.rgb_array = np.array(rgb_colors) / 255.0
        self.num_colors = len(rgb_colors)

    def to_magnitude(self, rgb_value):
        # Find the index of the closest RGB color
        idx = np.argmin(np.linalg.norm(self.rgb_array - (rgb_value / 255.0), axis=1))
        # Return the corresponding magnitude
        return idx + 1  # Assigning magnitudes starting from 1

with open("extracted_colors.json", "r") as file:
    extracted_colors = json.load(file)
extracted_colors.reverse()
# Convert RGB array to Matplotlib colormap
cmap = ListedColormap(np.array(extracted_colors) / 255.0)

url = "http://www.weather.gov.sg/files/rainarea/50km/v2/dpsri_70km_2024052514000000dBR.dpsri.png"
response = requests.get(url)
if response.status_code == 200:
    image_bytes = response.content
else:
    print("Failed to fetch data:", response.status_code)
# Convert PNG image to numpy array
image_b = np.array(image_bytes)
# Convert the image bytes to a PIL Image object
image = Image.open(io.BytesIO(image_bytes))
# Convert image to numpy array
rain_data = np.array(image)

min_lat, max_lat = 1.47, 1.14
min_lon, max_lon = 103.55, 104.1
num_rows, num_cols = rain_data.shape[:2]
# print(num_rows,num_cols) (120,217)
# print(rain_data.shape[0],rain_data.shape[1])
print(range(rain_data.shape[0]))
latitudes = np.linspace(min_lat, max_lat, num_rows)
longitudes = np.linspace(min_lon, max_lon, num_cols)
print(f"lat range:", latitudes.shape[0])
print("long range:", longitudes.shape[0])

features = []
geojson_data = {
    "type": "FeatureCollection",
    "features": []
}

# Map rain data to colormap
auto_cmap = AutoColormap(extracted_colors)
magnitude = np.empty([rain_data.shape[0],rain_data.shape[1]])
# Iterate over each pixel in the rain data and map RGB values to rain values
for i in range(num_rows):
  for j in range(num_cols):
      rgb_value = rain_data[i, j][0:3]
      print(i,j)
      if sum(rgb_value) == 0:
          magnitude[i,j] = np.NaN
      else:
          magnitude[i,j] = auto_cmap.to_magnitude(rgb_value)
        #   print(f"Pixel ({i}, {j}): RGB: {rgb_value}, Rain Value: {magnitude[i,j]}")
          feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [longitudes[j], latitudes[i]]  # Note: GeoJSON coordinates are (lon, lat)
                },
                "properties": {
                    "magnitude": magnitude[i,j]
                }
            }
          features.append(feature)
        #   print(feature)


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

# Plot the colormap and display the scalar values on the colorbar
plt.figure(figsize=(8, 6))
# plt.imshow(rain_data, cmap=cmap, aspect='auto')
plt.imshow(magnitude, cmap=cmap, aspect='auto')
plt.colorbar(label='Rain Magnitude')
plt.title('Rain Levels')
plt.show()
plt.savefig('rain_magnitude_plot.png')


