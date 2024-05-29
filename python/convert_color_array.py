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

class RainfallAnalyzer:
    def __init__(self, color_file):
        self.extracted_colors = self.load_colors(color_file)
        self.auto_cmap = AutoColormap(self.extracted_colors)
        self.cmap = ListedColormap(np.array(self.extracted_colors) / 255.0)
        self.min_lat, self.max_lat = 1.47, 1.14
        self.min_lon, self.max_lon = 103.55, 104.1

    def load_colors(self, color_file):
        with open(color_file, "r") as file:
            extracted_colors = json.load(file)
        extracted_colors.reverse()
        return extracted_colors

    def fetch_image(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            image_bytes = response.content
            return Image.open(io.BytesIO(image_bytes))
        else:
            raise Exception(f"Failed to fetch data: {response.status_code}")

    def analyze_rainfall(self, image):
        rain_data = np.array(image)
        num_rows, num_cols = rain_data.shape[:2]
        latitudes = np.linspace(self.min_lat, self.max_lat, num_rows)
        longitudes = np.linspace(self.min_lon, self.max_lon, num_cols)
        magnitude = np.empty([num_rows, num_cols])
        features = []

        for i in range(num_rows):
            for j in range(num_cols):
                rgb_value = rain_data[i, j][:3]
                if sum(rgb_value) == 0:
                    magnitude[i, j] = np.NaN
                else:
                    magnitude[i, j] = self.auto_cmap.to_magnitude(rgb_value)
                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [longitudes[j], latitudes[i]]
                        },
                        "properties": {
                            "magnitude": magnitude[i, j]
                        }
                    }
                    features.append(feature)
        
        return magnitude, features

    def save_geojson(self, features, output_file):
        geojson_data = {
            "type": "FeatureCollection",
            "features": features
        }
        with open(output_file, "w") as f:
            json.dump(geojson_data, f, indent=2)
        print("GeoJSON file saved:", output_file)

    def plot_magnitude(self, magnitude, output_file, title):
        plt.figure(figsize=(10, 6))
        plt.imshow(magnitude, cmap=self.cmap, aspect='auto')
        plt.colorbar(label='Rain Magnitude')
        plt.title(title)
        plt.show()
        plt.savefig(output_file)
        print("Plot saved:", output_file)

def main():
    color_file = "extracted_colors.json"
    month, day, year, time = "05", "27", "2024", "1400"
    
    rainfall_analyzer = RainfallAnalyzer(color_file)
    
    # Construct the URL for the image
    url = f"http://www.weather.gov.sg/files/rainarea/50km/v2/dpsri_70km_{year}{month}{day}{time}0000dBR.dpsri.png"
    image = rainfall_analyzer.fetch_image(url)
    
    # Analyze rainfall
    magnitude, features = rainfall_analyzer.analyze_rainfall(image)
    
    # Save results
    geojson_output_file = f"outputs/rainfall_magnitude_{year}{month}{day}{time}.geojson"
    rainfall_analyzer.save_geojson(features, geojson_output_file)
    
    plot_output_file = f"outputs/rain_magnitude_plot_{year}{month}{day}{time}.png"
    title = f'Rain Levels {year}/{month}/{day} Time: {time}'
    rainfall_analyzer.plot_magnitude(magnitude, plot_output_file, title)

if __name__ == "__main__":
    main()