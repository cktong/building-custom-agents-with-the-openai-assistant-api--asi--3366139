from PIL import Image
import numpy as np

# Load the JPEG image
image_path = "your_image.jpg"
image = Image.open(image_path)

# Convert the image to a NumPy array
image_array = np.array(image)

# Get the middle row of pixels from the image
middle_row_pixels = image_array[image_array.shape[0] // 2]

# Flatten the array to a 1D array for easier processing
middle_row_pixels_flat = middle_row_pixels.reshape(-1, middle_row_pixels.shape[-1])

# Extract unique colors from the middle row
unique_colors = np.unique(middle_row_pixels_flat, axis=0)

# Bin the unique colors into magnitude ranges
num_magnitudes = 10  # Define the number of magnitude bins
color_bins = np.array_split(unique_colors, num_magnitudes)

# Print the color bins
for i, color_bin in enumerate(color_bins):
    print(f"Magnitude {i+1}: {color_bin}")

# Now you have the unique colors binned according to their magnitude ranges
