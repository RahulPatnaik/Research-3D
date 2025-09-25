import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# File containing your block data
file_path = "/home/rahul/Desktop/BrickGPT/output.txt"

# Function to parse each line like "1x2 (7,17,0)"
def parse_line(line):
    line = line.strip()
    dims, coords = line.split(' ')
    w, h = map(int, dims.split('x'))
    x, y, z = map(int, coords.strip('()').split(','))
    return (w, h, x, y, z)

# Read all blocks
blocks = []
with open(file_path, 'r') as f:
    for line in f:
        if line.strip():
            blocks.append(parse_line(line))

# Function to create cuboid vertices and faces
def create_cuboid(x, y, z, dx, dy, dz=1):
    # Define the 8 vertices of the cuboid
    vertices = np.array([
        [x, y, z],
        [x+dx, y, z],
        [x+dx, y+dy, z],
        [x, y+dy, z],
        [x, y, z+dz],
        [x+dx, y, z+dz],
        [x+dx, y+dy, z+dz],
        [x, y+dy, z+dz]
    ])
    
    # Define the 6 faces of the cuboid (each face has 4 vertices)
    faces = [
        [vertices[0], vertices[1], vertices[2], vertices[3]],  # bottom
        [vertices[4], vertices[5], vertices[6], vertices[7]],  # top
        [vertices[0], vertices[1], vertices[5], vertices[4]],  # front
        [vertices[2], vertices[3], vertices[7], vertices[6]],  # back
        [vertices[1], vertices[2], vertices[6], vertices[5]],  # right
        [vertices[4], vertices[7], vertices[3], vertices[0]]   # left
    ]
    
    return faces

# Function to plot a cuboid
def plot_cuboid(ax, x, y, z, dx, dy, dz=1, color='skyblue'):
    faces = create_cuboid(x, y, z, dx, dy, dz)
    
    # Create a 3D polygon collection
    poly3d = Poly3DCollection(faces, alpha=0.7, facecolor=color, edgecolor='black')
    ax.add_collection3d(poly3d)

# Plotting
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Generate different colors for different blocks
colors = plt.cm.Set3(np.linspace(0, 1, len(blocks)))

for i, (w, h, x, y, z) in enumerate(blocks):
    plot_cuboid(ax, x, y, z, w, h, color=colors[i])

# Set axis labels and limits
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Block Visualization')

# Set equal aspect ratio and adjust view
max_range = max(max(x+w, y+h) for w, h, x, y, z in blocks)
ax.set_xlim(0, max_range)
ax.set_ylim(0, max_range)
ax.set_zlim(0, max(z for w, h, x, y, z in blocks) + 2)

ax.view_init(elev=30, azim=45)
plt.show()