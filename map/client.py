import socket
import pygame
import threading
import pickle

# Client setup
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", 5555))

# Prompt the player to enter their unique ID
player_id = input("Enter your player ID (e.g., 1 or 2): ")

# Send player ID to the server
client_socket.sendall(pickle.dumps(player_id))

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((400, 400))
clock = pygame.time.Clock()

player_positions = {}
labyrinth = None

# Grid size
GRID_SIZE = 20


# Function to receive updates from the server
def receive_updates():
    global player_positions, labyrinth
    while True:
        try:
            data = client_socket.recv(
                4096
            )  # Increased buffer size for larger maze data
            if data:
                player_positions, labyrinth = pickle.loads(data)
        except:
            break


# Function to send player position to the server
def send_position(position):
    data = pickle.dumps({player_id: position})
    client_socket.sendall(data)


# Start receiving updates from the server
threading.Thread(target=receive_updates).start()

# Initial player position
position = (1, 1)

# Game loop
running = True
while running:
    screen.fill((0, 0, 0))

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move player based on key presses
    keys = pygame.key.get_pressed()
    new_position = list(position)
    if keys[pygame.K_LEFT]:
        new_position[0] -= 1
    if keys[pygame.K_RIGHT]:
        new_position[0] += 1
    if keys[pygame.K_UP]:
        new_position[1] -= 1
    if keys[pygame.K_DOWN]:
        new_position[1] += 1

    # Ensure the player doesn't move into a wall
    if labyrinth is not None:  # Check if the labyrinth is initialized
        if (
            new_position[0] >= 0
            and new_position[0] < len(labyrinth)
            and new_position[1] >= 0
            and new_position[1] < len(labyrinth[0])
        ):
            if (
                labyrinth[new_position[0], new_position[1]] == 0
            ):  # Check if the new position is a path (0)
                position = tuple(new_position)

    # Send updated position to the server
    send_position(position)

    # Draw the labyrinth
    if labyrinth is not None:
        for x in range(len(labyrinth)):
            for y in range(len(labyrinth[x])):
                color = (255, 255, 255) if labyrinth[x, y] == 0 else (0, 0, 0)
                pygame.draw.rect(
                    screen, color, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                )

    # Draw all players
    for pid, pos in player_positions.items():
        color = (255, 0, 0) if pid == player_id else (0, 0, 255)
        pygame.draw.circle(
            screen,
            color,
            (pos[0] * GRID_SIZE + GRID_SIZE // 2, pos[1] * GRID_SIZE + GRID_SIZE // 2),
            10,
        )

    pygame.display.flip()
    clock.tick(30)

client_socket.close()
pygame.quit()
