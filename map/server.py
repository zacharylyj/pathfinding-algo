import socket
import threading
import pickle
import noise  # For generating Perlin noise
import numpy as np

# Define labyrinth dimensions
LABYRINTH_WIDTH = 20
LABYRINTH_HEIGHT = 20

# Player positions and labyrinth stored on the server
player_positions = {}
labyrinth = None  # Will be generated and sent to clients


# Function to generate a labyrinth using Perlin noise
def generate_labyrinth(width, height):
    scale = 10.0  # Controls the scale of the noise
    labyrinth = np.zeros((width, height))

    for x in range(width):
        for y in range(height):
            # Generate noise value between -1 and 1
            noise_value = noise.pnoise2(x / scale, y / scale, octaves=2)
            # Convert noise value to either wall (1) or path (0)
            if noise_value > 0:  # Threshold to decide wall or path
                labyrinth[x, y] = 1  # Wall
            else:
                labyrinth[x, y] = 0  # Path
    return labyrinth


# Function to broadcast updated positions and labyrinth to all clients
def broadcast_state(clients):
    for client in clients:
        try:
            # Send player positions and labyrinth state
            data = pickle.dumps((player_positions, labyrinth))
            client.sendall(data)
        except:
            clients.remove(client)


# Function to handle communication with a single client
def handle_client(client_socket, clients):
    global player_positions
    try:
        # Receive player ID from the client upon connection
        data = client_socket.recv(1024)
        player_id = pickle.loads(data)
        print(f"Player {player_id} connected.")
        player_positions[player_id] = (1, 1)  # Initialize player at position (1,1)

        # Send initial state (positions and labyrinth) to the client
        broadcast_state(clients)

        while True:
            # Receive updated position from the client
            data = client_socket.recv(1024)
            if not data:
                break
            position_update = pickle.loads(data)
            player_positions.update(position_update)

            # Broadcast updated positions to all clients
            broadcast_state(clients)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        # Remove player from position list when they disconnect
        if player_id in player_positions:
            del player_positions[player_id]
        broadcast_state(clients)


# Server to handle multiple clients and generate the labyrinth
def server():
    global labyrinth
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", 5555))
    server_socket.listen(5)

    # Generate labyrinth once when the server starts
    labyrinth = generate_labyrinth(LABYRINTH_WIDTH, LABYRINTH_HEIGHT)
    print("Labyrinth generated.")

    print("Server started, waiting for connections...")

    clients = []
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        clients.append(client_socket)

        # Start a new thread to handle the client
        threading.Thread(target=handle_client, args=(client_socket, clients)).start()


if __name__ == "__main__":
    server()
