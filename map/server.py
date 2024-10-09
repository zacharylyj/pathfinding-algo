import socket
import threading
import pickle
import numpy as np
from scipy.ndimage import label
from noise import pnoise2
import random

# Define the states for each cell
NO_WALL = 0
HORIZONTAL_WALL = 1
VERTICAL_WALL = 2
SLASH_FORWARD_WALL = 3
SLASH_BACKWARD_WALL = 4

# Maze dimensions
width, height = 1000, 1000

# Define region types
NORMAL = 0
DENSE = 1
WIDE = 2
LONG = 3
OPEN = 4
EXTRA_WIDE = 5

# Parameters for Perlin noise
octaves = 5
scale = 10.0
persistence = 0.5
lacunarity = 2.0

# Generate Perlin noise map
perlin_noise_map = np.zeros((height, width))
for y in range(height):
    for x in range(width):
        perlin_noise_map[y][x] = pnoise2(
            x / scale,
            y / scale,
            octaves=octaves,
            persistence=persistence,
            lacunarity=lacunarity,
            repeatx=width,
            repeaty=height,
            base=42,
        )

# Normalize Perlin noise to range between 0 and 1
perlin_noise_map = (perlin_noise_map - perlin_noise_map.min()) / (
    perlin_noise_map.max() - perlin_noise_map.min()
)

# Assign regions based on Perlin noise values
noise_map = np.full((height, width), NORMAL)  # Default all to NORMAL

# Label connected clusters in the Perlin noise map
clusters, num_clusters = label(perlin_noise_map < 0.5)

# Randomly assign a region type to each cluster
for cluster_num in range(1, num_clusters + 1):
    region_type = np.random.choice([DENSE, WIDE, LONG, OPEN, EXTRA_WIDE])
    noise_map[clusters == cluster_num] = region_type


# Function to generate walls based on the region type
def generate_walls_for_region(region_type):
    if region_type == NORMAL:
        return np.random.choice(
            [
                NO_WALL,
                HORIZONTAL_WALL,
                VERTICAL_WALL,
                SLASH_FORWARD_WALL,
                SLASH_BACKWARD_WALL,
            ],
            p=[0.2, 0.2, 0.2, 0.2, 0.2],
        )
    elif region_type == DENSE:
        return np.random.choice(
            [HORIZONTAL_WALL, VERTICAL_WALL, SLASH_FORWARD_WALL, SLASH_BACKWARD_WALL],
            p=[0.25, 0.25, 0.25, 0.25],
        )
    elif region_type == WIDE:
        return np.random.choice(
            [NO_WALL, HORIZONTAL_WALL, VERTICAL_WALL], p=[0.5, 0.25, 0.25]
        )
    elif region_type == LONG:
        return np.random.choice([NO_WALL, HORIZONTAL_WALL], p=[0.1, 0.9])
    elif region_type == OPEN:
        return NO_WALL
    elif region_type == EXTRA_WIDE:
        return np.random.choice(
            [NO_WALL, HORIZONTAL_WALL, VERTICAL_WALL], p=[0.7, 0.15, 0.15]
        )


# Generate the maze using the noise map to define wall types
maze = np.zeros((height, width), dtype=int)
for y in range(height):
    for x in range(width):
        maze[y, x] = generate_walls_for_region(noise_map[y, x])


# Function to find a valid starting position in the maze (a cell with NO_WALL)
def find_valid_start_position(maze):
    height, width = maze.shape
    while True:
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        if maze[y, x] == NO_WALL:  # Check if this is a walkable area
            return (x, y)


# Function to extract a section of the maze around the player
def get_maze_chunk(maze, center_x, center_y, chunk_size=50):
    half_chunk = chunk_size // 2
    min_x = max(center_x - half_chunk, 0)
    max_x = min(center_x + half_chunk, width)
    min_y = max(center_y - half_chunk, 0)
    max_y = min(center_y + half_chunk, height)

    return maze[min_y:max_y, min_x:max_x]


# Server to handle communication and send map chunks
def handle_client(client_socket):
    try:
        # Send the player their initial valid spawn point
        player_position = find_valid_start_position(maze)
        client_socket.sendall(pickle.dumps(player_position))

        while True:
            # Receive player's current position from client
            data = client_socket.recv(1024)
            if not data:
                break
            player_position = pickle.loads(data)

            # Send the relevant chunk of the maze based on the player's current position
            maze_chunk = get_maze_chunk(maze, player_position[0], player_position[1])
            client_socket.sendall(pickle.dumps(maze_chunk))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()


# Server setup
def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("localhost", 5555))
    server_socket.listen(5)
    print("Server started, waiting for connections...")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr}")
            threading.Thread(target=handle_client, args=(client_socket,)).start()
    except KeyboardInterrupt:
        print("Server is shutting down...")
    finally:
        server_socket.close()


if __name__ == "__main__":
    server()
