# Python file for handling game displaying

import pygame
import sys
import main
import gc
from os.path import exists

pygame.init()

# Functions and procedures for a chill life
def terminate():
    """Terminates the program."""
    pygame.quit() # Quits the pygame library
    sys.exit() # Quits the program

def update_state():
    """Updates the appearance of the game."""
    main.pygame.display.update() # Updates the display
    main.clock.tick(main.FPS) # Mimicks frame rate

def generate_tile(image_path, x, y):
    """Generates a tile onto the screen."""
    tile = pygame.image.load(image_path).convert_alpha() # Loads an image, removes transparency
    tile_fit = pygame.transform.scale(tile, (80, 80)) # Scales it to the tile's dimensions
    tile_rect = tile_fit.get_rect(topleft = (x, y)) # Creates an invisible rectangle using x and y coordinates
    main.screen.blit(tile_fit, tile_rect) # Displays an image onto the screen

def generate_background(image_path):
    """Generates a background onto the screen."""
    tile = pygame.image.load(image_path).convert_alpha()
    tile_fit = pygame.transform.scale(tile, (80, 80))
    for x in main.grid[0]: # For each tile space in a given row...
        for y in main.grid[1]: # For each tile space in a given column...
            tile_rect = tile_fit.get_rect(topleft = (x, y))
            main.screen.blit(tile_fit, tile_rect)

def garbage_disposal(garbage: list):
    """Disposes of all objects that are no longer needed."""
    for thing in garbage: # For each item in the list,
        del thing # Delete it
    gc.collect() # Free up space in memory

def update_file(file: str, info, line: int = 0):
    """Updates a file with information."""
    # If the file does not exist, create it
    file_copy = file # Avoids TypeError -> Opening file when it is already open

    # Check if the file exists and create a new file if not
    if not exists(file):
        with open(file, "w") as file:
            file.write("text")

    # Write data to a list version of the file
    with open(file_copy, "r") as filecopy:
        file_as_list = filecopy.readlines()

        # Either change the list data or add to it.
        try:
            file_as_list[line] = str(info) + "\n"
        except IndexError:
            file_as_list.insert(line, str(info) + "\n")

    # Write data to the file
    with open(file_copy, "w") as file:
        file.seek(0)
        for line in file_as_list:
            file.write(line)

