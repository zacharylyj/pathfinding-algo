import socket
import pygame
import pickle
import time

# Define the states for each cell (same as the server)
NO_WALL = 0
HORIZONTAL_WALL = 1
VERTICAL_WALL = 2
SLASH_FORWARD_WALL = 3
SLASH_BACKWARD_WALL = 4

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((800, 800))
clock = pygame.time.Clock()

# Grid size and chunk size
GRID_SIZE = 16
CHUNK_SIZE = 25  # Size of the chunk to request from the server, centered on player

# Player properties
PLAYER_RADIUS = 5
PLAYER_COLOR = (255, 0, 0)
PLAYER_SPEED = 2  # Speed of player movement
velocity = pygame.Vector2(0, 0)  # Player's velocity (initially 0)

# Colors for walls
WALL_COLOR = (0, 0, 0)

# Client setup
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", 5555))

# Receive initial player position from server
player_position = pygame.Vector2(
    *pickle.loads(client_socket.recv(1024))
)  # Player position as a vector
print(f"Player spawned at: {player_position}")

# Map chunk received from the server
maze_chunk = None


# Function to request and receive a chunk of the maze centered around the player
def request_maze_chunk(player_position):
    client_socket.sendall(
        pickle.dumps((int(player_position.x), int(player_position.y)))
    )
    data = client_socket.recv(16384)  # Increased buffer size for larger chunks
    return pickle.loads(data)


# Function to check if the player collides with any walls
def check_collision_with_walls(
    player_position, maze_chunk, chunk_offset_x, chunk_offset_y
):
    player_x, player_y = player_position.x, player_position.y
    # Translate chunk coordinates into global screen coordinates
    for y in range(len(maze_chunk)):
        for x in range(len(maze_chunk[y])):
            screen_x = (x - (CHUNK_SIZE // 2)) * GRID_SIZE + screen.get_width() // 2
            screen_y = (y - (CHUNK_SIZE // 2)) * GRID_SIZE + screen.get_height() // 2

            # Horizontal wall collision check
            if maze_chunk[y][x] == HORIZONTAL_WALL:
                if (
                    player_y + PLAYER_RADIUS > screen_y
                    and player_y - PLAYER_RADIUS < screen_y
                    and screen_x <= player_x <= screen_x + GRID_SIZE
                ):
                    return True

            # Vertical wall collision check
            elif maze_chunk[y][x] == VERTICAL_WALL:
                if (
                    player_x + PLAYER_RADIUS > screen_x
                    and player_x - PLAYER_RADIUS < screen_x
                    and screen_y <= player_y <= screen_y + GRID_SIZE
                ):
                    return True

            # Forward slash (/) wall collision check
            elif maze_chunk[y][x] == SLASH_FORWARD_WALL:
                if intersects_with_forward_slash(
                    player_x, player_y, screen_x, screen_y
                ):
                    return True

            # Backward slash (\) wall collision check
            elif maze_chunk[y][x] == SLASH_BACKWARD_WALL:
                if intersects_with_backward_slash(
                    player_x, player_y, screen_x, screen_y
                ):
                    return True

    return False  # No collision


# Function to check if the player intersects with a forward slash (/)
def intersects_with_forward_slash(player_x, player_y, line_x, line_y):
    # Forward slash (/) line: top-left to bottom-right
    dx = player_x - line_x
    dy = player_y - line_y
    return abs(dx - dy) < PLAYER_RADIUS


# Function to check if the player intersects with a backward slash (\)
def intersects_with_backward_slash(player_x, player_y, line_x, line_y):
    # Backward slash (\) line: top-right to bottom-left
    dx = player_x - line_x
    dy = player_y - line_y
    return abs(dx + dy - GRID_SIZE) < PLAYER_RADIUS


# Initial chunk request
maze_chunk = request_maze_chunk(player_position)

# Game loop
running = True
while running:
    screen.fill((255, 255, 255))  # White background

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get the player's input
    keys = pygame.key.get_pressed()
    velocity.x = 0
    velocity.y = 0

    if keys[pygame.K_LEFT]:
        velocity.x = -PLAYER_SPEED
    if keys[pygame.K_RIGHT]:
        velocity.x = PLAYER_SPEED
    if keys[pygame.K_UP]:
        velocity.y = -PLAYER_SPEED
    if keys[pygame.K_DOWN]:
        velocity.y = PLAYER_SPEED

    # Calculate the new position based on velocity
    new_position = player_position + velocity

    # Calculate chunk offset (where the chunk starts relative to the player)
    chunk_offset_x = int(player_position.x) - (CHUNK_SIZE // 2)
    chunk_offset_y = int(player_position.y) - (CHUNK_SIZE // 2)

    # Check for wall collisions before allowing movement
    if not check_collision_with_walls(
        new_position, maze_chunk, chunk_offset_x, chunk_offset_y
    ):
        player_position = new_position  # Apply the movement
        # Request new maze chunk when the player moves
        maze_chunk = request_maze_chunk(player_position)

    # Center player in the middle of the screen
    center_x, center_y = screen.get_width() // 2, screen.get_height() // 2

    # Draw the maze chunk around the player
    if maze_chunk is not None:
        for y in range(len(maze_chunk)):
            for x in range(len(maze_chunk[y])):
                # Calculate screen coordinates relative to the player's position
                screen_x = center_x + (x - (CHUNK_SIZE // 2)) * GRID_SIZE
                screen_y = center_y + (y - (CHUNK_SIZE // 2)) * GRID_SIZE

                if maze_chunk[y][x] == HORIZONTAL_WALL:
                    pygame.draw.line(
                        screen,
                        WALL_COLOR,
                        (screen_x, screen_y),
                        (screen_x + GRID_SIZE, screen_y),
                        2,
                    )
                elif maze_chunk[y][x] == VERTICAL_WALL:
                    pygame.draw.line(
                        screen,
                        WALL_COLOR,
                        (screen_x, screen_y),
                        (screen_x, screen_y + GRID_SIZE),
                        2,
                    )
                elif maze_chunk[y][x] == SLASH_FORWARD_WALL:
                    pygame.draw.line(
                        screen,
                        WALL_COLOR,
                        (screen_x, screen_y),
                        (screen_x + GRID_SIZE, screen_y + GRID_SIZE),
                        2,
                    )
                elif maze_chunk[y][x] == SLASH_BACKWARD_WALL:
                    pygame.draw.line(
                        screen,
                        WALL_COLOR,
                        (screen_x + GRID_SIZE, screen_y),
                        (screen_x, screen_y + GRID_SIZE),
                        2,
                    )

    # Draw the player as a dot in the center of the screen
    pygame.draw.circle(screen, PLAYER_COLOR, (center_x, center_y), PLAYER_RADIUS)

    pygame.display.flip()
    clock.tick(60)

client_socket.close()
pygame.quit()
