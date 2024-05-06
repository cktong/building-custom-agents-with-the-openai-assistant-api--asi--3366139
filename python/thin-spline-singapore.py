import json
import numpy as np
from tps import ThinPlateSpline
import matplotlib.pyplot as plt
import requests

# Load from data.gov.sg
url = "https://api.data.gov.sg/v1/environment/rainfall"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print("Data saved successfully.")
else:
    print("Failed to fetch data:", response.status_code)

# Test: Load data from JSON file
# with open("weather_data.json", "r") as file:
#     data = json.load(file)

# Extract station locations and rainfall values
stations = data["metadata"]["stations"]
station_locations = np.array([(station["location"]["latitude"], station["location"]["longitude"]) for station in stations])
rainfall_values = np.array([reading["value"] for reading in data["items"][0]["readings"]])

# Find northernmost, southernmost, westernmost, and easternmost stations
north = np.max(station_locations[:, 0])
south = np.min(station_locations[:, 0])
west = np.min(station_locations[:, 1])
east = np.max(station_locations[:, 1])

# Create a grid covering the area defined by the outermost stations
grid_lat = np.linspace(south, north, 100)  # Define latitude range
grid_lon = np.linspace(west, east, 100)  # Define longitude range
grid_points = np.array(np.meshgrid(grid_lat, grid_lon)).reshape(2, -1).T

# Fit TPS model
tps = ThinPlateSpline(alpha=0.0)
tps.fit(station_locations, rainfall_values)

# Transform grid points
estimated_rainfall = tps.transform(grid_points)

# Reshape estimated rainfall to match grid shape
estimated_grid_transposed = estimated_rainfall.reshape(len(grid_lat), len(grid_lon)).T
estimated_rainfall_grid = np.flip(estimated_grid_transposed, axis=0)

# Clip negative values
estimated_rainfall_grid[estimated_rainfall_grid < 0] = 0

# Load Singapore boundary from GeoJSON file
with open("singapore_boundary.geojson", "r") as file:
    singapore_boundary_data = json.load(file)
# Extract boundary coordinates
boundary_coordinates = np.array(singapore_boundary_data["geometry"]["coordinates"][0])

# Plot rain map
plt.figure(figsize=(10, 8))
plt.imshow(estimated_rainfall_grid, extent=[grid_lon.min(), grid_lon.max(), grid_lat.min(), grid_lat.max()])
plt.plot(boundary_coordinates[:, 0], boundary_coordinates[:, 1], color='red', linewidth=2)  # Plot Singapore boundary
plt.colorbar(label='Estimated Rainfall (mm)')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Estimated Rainfall Map of Singapore')

# Plot weather stations
plt.scatter(station_locations[:, 1], station_locations[:, 0], color='red', marker='.', label='Weather Stations')

plt.show()
plt.savefig('singapore_rain.png')

output_data = []
for i in range(len(grid_lat)):
    for j in range(len(grid_lon)):
        output_data.append({
            "latitude": grid_lat[i],
            "longitude": grid_lon[j],
            "estimated_rainfall": estimated_rainfall_grid[i][j]
        })

# Save estimated rainfall grid to JSON file
with open("outputs/estimated_rainfall.json", "w") as outfile:
    json.dump(output_data, outfile, indent=4)
