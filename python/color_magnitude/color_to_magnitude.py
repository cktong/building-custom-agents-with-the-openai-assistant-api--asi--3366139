from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import json

# Load the JPEG image
image_path = "color_magnitude.jpeg"
image = Image.open(image_path)

# Convert the image to a NumPy array
image_array = np.array(image)

# Get the middle row of pixels from the image
middle_row_pixels = image_array[image_array.shape[0] // 2]

# Flatten the array to a 1D array for easier processing
middle_row_pixels_flat = middle_row_pixels.reshape(-1, middle_row_pixels.shape[-1])
size_of_middle_row = len(middle_row_pixels_flat)
print("Size of middle_row_pixels_flat:", size_of_middle_row)

# Starting index for iteration
start_index = 6

# Step size for iteration
step_size = 12

# Initialize an empty list to store colors
colors_list = []

# Iterate through every 12th pixel starting at index 6
for i in range(start_index, len(middle_row_pixels_flat), step_size):
    # Get the color of the pixel at index i
    color = middle_row_pixels_flat[i]
    # Append the color to the list
    colors_list.append(color)

# Display the list of colors
print("Colors extracted from middle row pixels:", colors_list)

# Plot the colors
plt.figure(figsize=(8, 1))
plt.imshow([colors_list], aspect='auto')
plt.title('Extracted Colors')
plt.xlabel('Pixel Index')
plt.yticks([])
plt.show()
plt.savefig('color_magnitude.png')

# Convert the numpy array to a standard Python list
colors_list = middle_row_pixels_flat.tolist()

# Save the colors to a JSON file
with open('extracted_colors.json', 'w') as file:
    json.dump(colors_list, file)