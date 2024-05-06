import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from tps import ThinPlateSpline

# Some data
X_c = np.random.normal(0, 1, (800, 3))  # Control points in 3D space
X_t = np.random.normal(0, 2, (800, 2))  # Target points in 3D space
X = np.random.normal(0, 1, (300, 3))     # New points in 3D space

# Create the tps object
tps = ThinPlateSpline(alpha=0.0)  # 0 Regularization

# Fit the control and target points
tps.fit(X_c, X_t)

# Transform new points
Y = tps.transform(X)

# Plotting
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Original points (Control and Target)
ax.scatter(X_c[:, 0], X_c[:, 1], X_c[:, 2], color='blue', label='Control Points')
ax.scatter(X_t[:, 0], X_t[:, 1], X_t[:, 1], color='red', label='Target Points')

# Transformed points
ax.scatter(Y[:, 0], Y[:, 1], Y[:, 1], color='green', label='Transformed Points')

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('Thin Plate Spline Transformation')
ax.legend()

# Save the plot as a PNG file
plt.savefig('tps_plot_3d.png')

# Show the plot
plt.show()

