# Main file

import pygame
import game
import random
import sounds
import inspect
import enemy

from os.path import join, exists

# Initialising pygame library
pygame.init()
pygame.mixer.init()

# Colour setup: (R, G, B)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLACK = (0, 0, 0)

# General purpose functions and procedures

# Sprite selection
def get_sprite_sheet(path, frame):
    """Returns part of a sprite sheet."""
    image = pygame.image.load(path).convert_alpha() # Get the image
    desired_frame = image.subsurface(pygame.Rect(frame)) # Create a surface from the image using the frame (x, y, width, height)
    return desired_frame

# Updating the sounds
def update_sounds(file, mode = "write", volume1 = None, volume2 = None):
    """Updates and saves the volume of sounds."""
    global narrator_volume, sound_volume
    
    # Creates the file if it doesn't exist - it would be assumed that we would be writing to the file
    if not exists(file):
        with open(file, "w") as file_copy:
            file_copy.write("text")
            game.update_file(file_copy, narrator_volume)
            game.update_file(file_copy, sound_volume, line=1)
            print("Mode functionality denied. Re-call function.")
            return

    # If we want to read from the file, read from it and update the volume accordingly
    if mode.lower() == "read":
        with open(file, "r") as sound_data:
            sound_data_copy = sound_data.readlines()

            narrator_volume = float(sound_data_copy[0].replace("\n", ""))
            sound_volume = float(sound_data_copy[1].replace("\n", ""))
            
    # If we want to write to the file, write to it and save the data accordingly
    if mode.lower() == "write" and (volume1 is not None and volume2 is not None):
        game.update_file(file, narrator_volume)
        game.update_file(file, sound_volume, line=1)

# Class variables

# Text setup
class Text():
    def __init__(self, contents: str, x: int, y: int, size: int, colour: tuple = WHITE):
        """A customisable Text class that piggybacks off the existing Pygame text class."""
        main_font = pygame.font.Font(join("Assets", "Fonts", "pixel_pirate.ttf"), size) # Font object, font can be used commercially
        self.font = main_font
        self.contents = contents
        self.x = x
        self.y = y
        self.text = main_font.render(contents, True, colour)
        self.rect = self.text.get_rect(center = (x, y))

    def update(self):
        """Displays the text onto the current screen."""
        screen.blit(self.text, self.rect)

# Button setup
class Button(pygame.sprite.Sprite):
    def __init__(self, image: str, text_contents: str, text_size: int, x: int, y: int, width: int, height: int, colour: tuple = WHITE):
        """Generates a cool button that a user can interact with."""
        super().__init__()
        self.image_normal = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image_normal, (width, height))
        self.text_font = pygame.font.Font(join("Assets", "Fonts", "pixel_pirate.ttf"), text_size)
        self.text = self.text_font.render(text_contents, True, colour)
        self.rect = self.image.get_rect(center = (x, y))
        self.text_rect = self.text.get_rect(center = (x, y))

    def update(self):
        """Add button with text on top."""
        screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

# Level setup
class Level(pygame.sprite.Sprite):
    def __init__(self, level_number: str, x: int, y: int, level_func, locked: bool = False):
        """Creates a level object that the user can select."""
        super().__init__()
        self.text = pygame.font.Font(join("Assets", "Fonts", "pixel_pirate.ttf"), 40)
        self.num = self.text.render(level_number, True, (255, 255, 255))
        self.x = x
        self.y = y
        self.level_func = level_func
        self.locked = locked
        self.index = 0
        self.frames = [join("Assets", "Buttons", "levelbutton.png"),
                       join("Assets", "Buttons", "levellocked.png")]
        self.image_small = pygame.image.load(self.frames[self.index]).convert_alpha()
        self.image = pygame.transform.scale(self.image_small, (SQUARE_LENGTH * 1.5, SQUARE_LENGTH * 1.5))
        self.rect = self.image.get_rect(center = (x, y))
        self.text_rect = self.num.get_rect(center= (x, y))

    def go_to_level(self, mouse_pos: list[int]):
        """Goes to the level that the object represents."""
        if self.rect.collidepoint(mouse_pos) and not self.locked: # If the level is pressed and is not locked...
            level_select.play()
            self.level_func() # Go to the level

    def lock(self):
        """Locks the level."""
        self.locked = True

    def unlock(self):
        """Unlocks the level."""
        self.locked = False

    def update(self):
        """Updates the object"""
        # If the level isn't locked, show it. Else, show it.
        if not self.locked:
            self.index = 0
            self.image_small = pygame.image.load(self.frames[self.index]).convert_alpha()
            self.image = pygame.transform.scale(self.image_small, (SQUARE_LENGTH * 1.5, SQUARE_LENGTH * 1.5))
            screen.blit(self.image, self.rect)
            screen.blit(self.num, (self.text_rect))
        else:
            self.index = 1
            self.image_small = pygame.image.load(self.frames[self.index]).convert_alpha()
            self.image = pygame.transform.scale(self.image_small, (SQUARE_LENGTH * 1.5, SQUARE_LENGTH * 1.5))
            screen.blit(self.image, self.rect)

# Functions related to above class
def get_unlocked_level_number(levels) -> int:
    """Calculates the number of unlocked levels."""
    # Stores the number of unlocked levels.
    unlocked_count: int = 0

    # For each level, check if the level is accessible to the player or not.
    for level in levels:
        if not level.locked:
            unlocked_count += 1

    return unlocked_count

def reset_levels(levels, completion_count: int = 1):
    """Resets all the levels such that the player can only access level 1."""
    # For each level, make them unlocked apart from the first one.
    for idx, level in enumerate(levels):
        if idx <= completion_count - 1: # If 2 levels are completed, unlock levels at index 0 and index 1
            level.locked = False
        else:
            level.locked = True

def load_data_from_game_file(filename="gamedata.txt"):
    """Loads the data from the game file."""

    cleaned_file = [] # List represenation of cleaned version of file

    # If the file exists, read its data
    if exists(filename):
        with open(filename, "r") as game_file:
            game_data = game_file.readlines()
            # Remove any trailing newline characters so the item is purely there
            for data in game_data:
                data_clean = data.strip("\n")
                cleaned_file.append(data_clean)

        # Unlock all the levels accordingly
        reset_levels(list_of_levels, int(cleaned_file[0]))

    else:
        # Unlock the first level only
        reset_levels(list_of_levels, 1)
  
# Player setup
class Player(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        """Creates a player object that a user can control."""
        super().__init__()
        self.image_path = join("Assets", "Player", "PlayerSprite.png")
        self.image_path_2 = join("Assets", "Player", "PlayerLose.png")
        # 1st set of images for player, 2nd set of images for player lose state
        self.images_1 = [get_sprite_sheet(self.image_path, (0, 0, 16, 16)),
                        get_sprite_sheet(self.image_path, (16, 0, 16, 16))]
        
        self.images_2 = [get_sprite_sheet(self.image_path_2, (0, 0, 16, 16)),
                         get_sprite_sheet(self.image_path_2, (16, 0, 16, 16)),
                         get_sprite_sheet(self.image_path_2, (32, 0, 16, 16)),
                         get_sprite_sheet(self.image_path_2, (48, 0, 16, 16))]
        self.index = 0
        self.image_normal = self.images_1[self.index].convert_alpha()
        self.image = pygame.transform.scale(self.image_normal, (SQUARE_LENGTH, SQUARE_LENGTH))
        self.x = x
        self.y = y
        self.rect = self.image.get_rect(topleft = (self.x, self.y))

        # Attributes for movement
        self.dy = 0
        self.dx = 0
        self.current_frame = 0
        self.target_frame = 10
        self.moving = False

        # Attributes for losing
        self.loss = False
        self.loss_sound = False
        self.loss_animation = False

    def movement(self, event):
        """Holds the code required to move the player and puts it in the main game loop."""

        # If WASD is pressed and the player isn't moving or in a lose state..
        if event.type == pygame.KEYDOWN and not self.moving and not self.loss:
            
            # Move the player according to the button they press in a smooth manner
            if event.key == pygame.K_w:
                self.dy = -(SQUARE_LENGTH / self.target_frame)
                self.dx = 0
                self.current_frame = 0
                self.moving = True
                self.set_image(0)
                player_move_sound.play()

            if event.key == pygame.K_s:
                self.dy = (SQUARE_LENGTH / self.target_frame)
                self.dx = 0
                self.current_frame = 0
                self.moving = True
                self.set_image(1)
                player_move_sound.play()

            if event.key == pygame.K_a:
                self.dy = 0
                self.dx = -(SQUARE_LENGTH / self.target_frame)
                self.current_frame = 0
                self.moving = True
                self.set_image(1)
                player_move_sound.play()

            if event.key == pygame.K_d:
                self.dy = 0
                self.dx = (SQUARE_LENGTH / self.target_frame)
                self.current_frame = 0
                self.moving = True
                self.set_image(0)
                player_move_sound.play()

    def set_loss(self, loss):
        """Finds out if the player has entered a lose state."""

        # If the player has not lost, do nothing. Otherwise, set the attribute relating to losing as True.
        if not loss:
            pass

        else:
            self.loss = True
            self.loss_sound = True
            self.loss_animation = True       

    def set_image(self, index: int):
        """Sets the image of the player"""
        self.image_normal = self.images_1[index].convert_alpha()
        self.image = pygame.transform.scale(self.image_normal, (SQUARE_LENGTH, SQUARE_LENGTH))

    def set_image_loss(self, index: int):
        """Sets the image of the player when losing."""
        self.image_normal = self.images_2[index].convert_alpha()
        self.image = pygame.transform.scale(self.image_normal, (SQUARE_LENGTH, SQUARE_LENGTH))

    def update(self):
        """Updates the player sprite."""

        # Play the sound if the player has lost.
        if self.loss_sound:

            # 20% to play a narrator voice line if the player has lost
            if random.randint(0, 4) == 1:
                lose_narrator_sound = pygame.mixer.Sound(random.choice(sounds.lose_state_sounds))
                lose_narrator_sound.set_volume(narrator_volume)
                lose_narrator_sound.play()

            lose_sound.play()
            self.loss_sound = False

        # If the player is losing, show it
        if self.loss:
            self.index += 0.2

            # Ensure the index is existing
            if not 0 <= self.index < len(self.images_2):
                self.index = 0

                # Tell the game that the animation has played in its entirety
                self.loss_animation = False
            
            else:
                # Set the image of the player
                self.set_image_loss(int(self.index))

# Wall setup
class Wall(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        """Creating a wall object that acts as a barrier for the player."""
        super().__init__()
        self.image_normal = pygame.image.load(join("Assets", "Block", "Block.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image_normal, (SQUARE_LENGTH, SQUARE_LENGTH))
        self.rect = self.image.get_rect(topleft = (x, y))

    def check_collision(self, moving_thing):
        """Checks if a moving thing is colliding with the wall."""
        if moving_thing.dx > 0: # If the moving thing is moving right...
            if moving_thing.rect.collidepoint(self.rect.midleft): # If the moving thing is colliding with the left of the wall..
                # Make sure the moving thing does not go through the wall and make sure the moving thing is moving no more
                moving_thing.rect.x = self.rect.x - 80
                moving_thing.dx = 0
                moving_thing.dy = 0
        if moving_thing.dx < 0:
            if moving_thing.rect.collidepoint(self.rect.midright):
                moving_thing.rect.x = self.rect.x + 80
                moving_thing.dx = 0
                moving_thing.dy = 0
        if moving_thing.dy > 0:
            if moving_thing.rect.collidepoint(self.rect.midtop):
                moving_thing.rect.y = self.rect.y - 80
                moving_thing.dx = 0
                moving_thing.dy = 0
        if moving_thing.dy < 0:
            if moving_thing.rect.collidepoint(self.rect.midbottom):
                moving_thing.rect.y = self.rect.y + 80
                moving_thing.dx = 0
                moving_thing.dy = 0
    
def wall_factory(wall_list: list) -> list[Wall]:
    """Creates walls based on a list of walls. """
    wall_object_list = []
    for wall in wall_list: # For each wall in the list
        # Grid reference
        x = wall[0] * SQUARE_LENGTH
        y = wall[1] * SQUARE_LENGTH
        # Add it to the list; once all walls are put into the list, return it
        wall_object_list.append(Wall(x, y))
    return wall_object_list

# Win setup
class Win(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        """A win block that when the player is on it, the player 'wins'."""
        super().__init__()
        self.image_path = join("Assets", "Block", "WinBlock.png")
        self.images = [get_sprite_sheet(self.image_path, (0, 0, 16, 16)),
                       get_sprite_sheet(self.image_path,(16, 0, 16, 16)),
                       get_sprite_sheet(self.image_path,(32, 0, 16, 16)),
                       get_sprite_sheet(self.image_path,(48, 0, 16, 16))]
        self.index = 0
        self.image_normal = self.images[int(self.index)].convert_alpha()
        self.image = pygame.transform.scale(self.image_normal, (SQUARE_LENGTH, SQUARE_LENGTH))
        self.rect = self.image.get_rect(topleft = (x,y))

    def update(self):
        """Animations!"""
        # Loop the animation
        if self.index >= len(self.images) - 1:
            self.index = 0
        # Increase the index to change the animation and then redefine the image
        self.index += (1/10)
        self.image_normal = self.images[int(self.index)].convert_alpha()
        self.image = pygame.transform.scale(self.image_normal, (SQUARE_LENGTH, SQUARE_LENGTH))

# ----------------------------------------------------------------------- #

# Levels 

def not_implemented():
    # Inspect looks at live objects
    # current_frame looks at the current caller in the stack
    # f_code looks at the the called object
    # co_name is the name of said called object

    current_function = inspect.currentframe().f_code.co_name
    raise NotImplementedError(f"'{current_function.upper()}' is not implemented.")

def abstract_level_layout():
    """DO NOT CALL"""
    player = Player(grid[0][3], grid[1][5])

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.terminate()
            player.movement(event)

        game.update_state()

def level_1(paused = False, reload_paused = False):
    """Level one"""

    global index_list, object_coordinates

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA) # Overlays the level translucent
    overlay.fill((10, 10, 10)) # Grey
    overlay_rect = overlay.get_rect(topleft = (0, 0))

    # Introductory sound to provoke the user to move the player around
    narrator = pygame.mixer.Sound(sounds.level_with_only_player_sounds[4])
    narrator.set_volume(narrator_volume)
    text = Text("Use the W, A, S and D keys to move.", WIDTH//2, HEIGHT//4, 30) # Text matching voice line

    # Load in all object in normal positions
    if not paused:

        player = Player(grid[0][5], grid[1][4])
        win = Win(grid[0][10], grid[1][4])
        pause = Button(back_button, "", 30, WIDTH - 50, 50, SQUARE_LENGTH, SQUARE_LENGTH)

        level_group = pygame.sprite.Group()
        level_group.add(win, player, pause,
                        wall_factory([[x, 3] for x in range(4, 12)]),
                        wall_factory([[4, 4], [11, 4]]),
                        wall_factory([[x, 5] for x in range(4, 12)]))
        
        narrator.play() # Play the sound 
    
    # Load in objects at last known coordinates based upon the index list's preference
    elif paused:

        # Define player x and y positions, using index list to find right recursive array position
        player_x = object_coordinates[index_list[0]][0]
        player_y = object_coordinates[index_list[0]][1]
        
        player = Player(player_x, player_y)
        win = Win(grid[0][10], grid[1][4])
        pause = Button(back_button, "", 30, WIDTH - 50, 50, SQUARE_LENGTH, SQUARE_LENGTH)

        level_group = pygame.sprite.Group()
        level_group.add(win, player, pause,
                        wall_factory([[x, 3] for x in range(4, 12)]),
                        wall_factory([[4, 4], [11, 4]]),
                       wall_factory([[x, 5] for x in range(4, 12)]))
        
        index_list = []
        object_coordinates = [[]]
        
    # Go back to the pause menu and load the objects to the screen
    if reload_paused:
        #game.generate_background(background1)
        #level_group.draw(screen) <-- Bug

        # Fixes the flashing bug
        overlay.set_alpha(10)
        screen.blit(overlay, overlay_rect)

        index_list = [0]
        object_coordinates = [[player.rect.x, player.rect.y]]
        pause_menu(level_1)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.terminate()
            player.movement(event) # Check for the player movement
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if pause.rect.collidepoint(event.pos) and not player.moving:
                        game.garbage_disposal([level_group]) # Free up the memory
                        menu_forward.play()
                        index_list = [0] # Look at first index first
                        object_coordinates = [[player.rect.x, player.rect.y]] # Coordinates of all MOVING objects
                        pause_menu(level_1) # The game is paused

        if player.current_frame < player.target_frame: # If the player is not done moving...
            player.rect.y += player.dy # Update the y position
            player.rect.x += player.dx # Update the x position
            for wall in level_group: # For each wall in the group...
                if isinstance(wall, Wall): # Checks if the "wall" is a wall
                    wall.check_collision(player)
            player.current_frame += 1 # Increment the current frame

        # If the player wins, load the win menu
        if player.rect == win.rect:
            game.garbage_disposal([player, win, level_group])
            narrator.stop()
            win_menu(level_1)
        
        # If the player has completed moving, then tell the game that they are no longer moving
        if player.current_frame >= player.target_frame:
            player.moving = False

        game.generate_background(background1)

        level_group.update()
        level_group.draw(screen)

        text.update()

        game.update_state()

def level_2(paused = False, reload_paused = False):
    global index_list, object_coordinates

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA) # Overlays the level translucent
    overlay.fill((10, 10, 10)) # Grey
    overlay_rect = overlay.get_rect(topleft = (0, 0))

    # Load in all object in normal positions
    if not paused:

        player = Player(grid[0][2], grid[1][4])
        win = Win(grid[0][6], grid[1][4])
        pause = Button(back_button, "", 30, WIDTH - 50, 50, SQUARE_LENGTH, SQUARE_LENGTH)

        level_group = pygame.sprite.Group()
        level_group.add(win, player, pause,
                        wall_factory([[x, 2] for x in range(1, 8)]),
                        wall_factory([[x, 6] for x in range(1, 8)]),
                        wall_factory([[1, y] for y in range(3, 6)]),
                        wall_factory([[7, y] for y in range(3, 6)]),
                        wall_factory([[4, 4]]))
        
        # Play a random sound 20% of the time
        if random.randint(0, 4) == 3:
            level_with_only_player_sounds_copy = sounds.level_with_only_player_sounds[:4] # Copy of list without the last voice line
            narrator = pygame.mixer.Sound(random.choice(level_with_only_player_sounds_copy)) # Random choice of voiceline
            narrator.set_volume(narrator_volume)
            narrator.play()
        
    # Load in objects at last known coordinates based upon the index list's preference
    elif paused:

        # Define player x and y positions, using index list to find right recursive array position
        player_x = object_coordinates[index_list[0]][0]
        player_y = object_coordinates[index_list[0]][1]
        
        player = Player(player_x, player_y)
        win = Win(grid[0][6], grid[1][4])
        pause = Button(back_button, "", 30, WIDTH - 50, 50, SQUARE_LENGTH, SQUARE_LENGTH)

        level_group = pygame.sprite.Group()
        level_group.add(win, player, pause,
                        wall_factory([[x, 2] for x in range(1, 8)]),
                        wall_factory([[x, 6] for x in range(1, 8)]),
                        wall_factory([[1, y] for y in range(3, 6)]),
                        wall_factory([[7, y] for y in range(3, 6)]),
                        wall_factory([[4, 4]]))
        
        index_list = []
        object_coordinates = [[]]
        
    # Go back to the pause menu and load the objects to the screen
    if reload_paused:
        #game.generate_background(background1)
        #level_group.draw(screen) <-- Bug

        # Fixes the flashing bug
        overlay.set_alpha(10)
        screen.blit(overlay, overlay_rect)

        index_list = [0]
        object_coordinates = [[player.rect.x, player.rect.y]]
        pause_menu(level_2)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.terminate()
            player.movement(event) # Check for the player movement
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if pause.rect.collidepoint(event.pos) and not player.moving:
                        game.garbage_disposal([level_group]) # Free up the memory
                        menu_forward.play()
                        index_list = [0] # Look at first index first
                        object_coordinates = [[player.rect.x, player.rect.y]] # Coordinates of all MOVING objects
                        pause_menu(level_2) # The game is paused

        if player.current_frame < player.target_frame: # If the player is not done moving...
            player.rect.y += player.dy # Update the y position
            player.rect.x += player.dx # Update the x position
            for wall in level_group: # For each wall in the group...
                if isinstance(wall, Wall): # Checks if the "wall" is a wall
                    wall.check_collision(player)
            player.current_frame += 1 # Increment the current frame

        if player.rect == win.rect:
            game.garbage_disposal([player, win, level_group])
            win_menu(level_2)
        
        # If the player has completed moving, then tell the game that they are no longer moving
        if player.current_frame >= player.target_frame:
            player.moving = False

        game.generate_background(background1)

        level_group.update()
        level_group.draw(screen)

        game.update_state()

def level_3(paused = False, reload_paused = False):
    """Level 3"""
    global index_list, object_coordinates

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA) # Overlays the level translucent
    overlay.fill((10, 10, 10)) # Grey
    overlay_rect = overlay.get_rect(topleft = (0, 0))

    # Load in all object in normal positions
    if not paused:

        player = Player(grid[0][4], grid[1][2])
        win = Win(grid[0][11], grid[1][6])
        pause = Button(back_button, "", 30, WIDTH - 50, 50, SQUARE_LENGTH, SQUARE_LENGTH)

        level_group = pygame.sprite.Group()
        level_group.add(win, player, pause,
                        wall_factory([[x, 1] for x in range(3, 13)]),
                        wall_factory([[x, 7] for x in range(3, 13)]),
                        wall_factory([[3, y] for y in range(2, 8)]),
                        wall_factory([[12, y] for y in range(2, 8)]),
                        wall_factory([[x, 6] for x in range(4, 11)]),
                        wall_factory([[x, 2] for x in range(5, 12)]),
                        wall_factory([[x, 3] for x in range(5, 9)]),
                        wall_factory([[10, y] for y in range(4, 6)]),
                        wall_factory([[9, 5], [7, 4], [5, 5]])
                        )
        
        # Play a random sound 20% of the time
        if random.randint(0, 4) == 3:
            level_with_only_player_sounds_copy = sounds.level_with_only_player_sounds[:4] # Copy of list without the last voice line
            narrator = pygame.mixer.Sound(random.choice(level_with_only_player_sounds_copy)) # Random choice of voiceline
            narrator.set_volume(narrator_volume)
            narrator.play()
                        
        
    # Load in objects at last known coordinates based upon the index list's preference
    elif paused:

        # Define player x and y positions, using index list to find right recursive array position
        player_x = object_coordinates[index_list[0]][0]
        player_y = object_coordinates[index_list[0]][1]
        
        player = Player(player_x, player_y)
        win = Win(grid[0][11], grid[1][6])
        pause = Button(back_button, "", 30, WIDTH - 50, 50, SQUARE_LENGTH, SQUARE_LENGTH)

        level_group = pygame.sprite.Group()
        level_group.add(win, player, pause,
                        wall_factory([[x, 1] for x in range(3, 13)]),
                        wall_factory([[x, 7] for x in range(3, 13)]),
                        wall_factory([[3, y] for y in range(2, 8)]),
                        wall_factory([[12, y] for y in range(2, 8)]),
                        wall_factory([[x, 6] for x in range(4, 11)]),
                        wall_factory([[x, 2] for x in range(5, 12)]),
                        wall_factory([[x, 3] for x in range(5, 9)]),
                        wall_factory([[10, y] for y in range(4, 6)]),
                        wall_factory([[9, 5], [7, 4], [5, 5]])
                        )
        
        index_list = []
        object_coordinates = [[]]
        
    # Go back to the pause menu and load the objects to the screen
    if reload_paused:
        #game.generate_background(background1)
        #level_group.draw(screen) <-- Bug

        # Fixes the flashing bug
        overlay.set_alpha(10)
        screen.blit(overlay, overlay_rect)

        index_list = [0]
        object_coordinates = [[player.rect.x, player.rect.y]]
        pause_menu(level_3)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.terminate()
            player.movement(event) # Check for the player movement
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if pause.rect.collidepoint(event.pos) and not player.moving:
                        game.garbage_disposal([level_group]) # Free up the memory
                        menu_forward.play()
                        index_list = [0] # Look at first index first
                        object_coordinates = [[player.rect.x, player.rect.y]] # Coordinates of all MOVING objects
                        pause_menu(level_3) # The game is paused

        if player.current_frame < player.target_frame: # If the player is not done moving...
            player.rect.y += player.dy # Update the y position
            player.rect.x += player.dx # Update the x position
            for wall in level_group: # For each wall in the group...
                if isinstance(wall, Wall): # Checks if the "wall" is a wall
                    wall.check_collision(player)
            player.current_frame += 1 # Increment the current frame

        if player.rect == win.rect:
            game.garbage_disposal([player, win, level_group])
            win_menu(level_3)
        
        # If the player has completed moving, then tell the game that they are no longer moving
        if player.current_frame >= player.target_frame:
            player.moving = False

        game.generate_background(background1)

        level_group.update()
        level_group.draw(screen)

        game.update_state()
    
def level_4(paused = False, reload_paused = False):
    """Level 4"""
    global index_list, object_coordinates

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA) # Overlays the level translucent
    overlay.fill((10, 10, 10)) # Grey
    overlay_rect = overlay.get_rect(topleft = (0, 0))

    # Load in all object in normal positions
    if not paused:

        player = Player(grid[0][1], grid[1][5])
        win = Win(grid[0][9], grid[1][3])
        pause = Button(back_button, "", 30, WIDTH - 50, 50, SQUARE_LENGTH, SQUARE_LENGTH)

        level_group = pygame.sprite.Group()
        level_group.add(win, player, pause,
                        wall_factory([[x, 2] for x in range(0, 17)]), # Top wall barrier
                        wall_factory([[x, 6] for x in range(0, 17)]), # Bottom wall barrier
                        wall_factory([[0, y] for y in range(3, 6)]), # Left wall barrier
                        wall_factory([[15, y] for y in range(3, 6)]), # Rightwall barrier
                        wall_factory([[2, 4], [2, 5]]), # First rectangle barrier
                        wall_factory([[4, 3], [4, 4]]), # Second rectangle barrier
                        wall_factory([[6, 4], [6, 5]]), # Third rectangle barrier
                        wall_factory([[8, 3]]), # Singular barrier preventing from going to the goal
                        wall_factory([[x, 4] for x in range(8, 14)]) # Long barrier making journey to goal tedious
                        )
        
        # Play a random sound 20% of the time
        if random.randint(0, 4) == 3:
            level_with_only_player_sounds_copy = sounds.level_with_only_player_sounds[:4] # Copy of list without the last voice line
            narrator = pygame.mixer.Sound(random.choice(level_with_only_player_sounds_copy)) # Random choice of voiceline
            narrator.set_volume(narrator_volume)
            narrator.play()
        
    # Load in objects at last known coordinates based upon the index list's preference
    elif paused:

        # Define player x and y positions, using index list to find right recursive array position
        player_x = object_coordinates[index_list[0]][0]
        player_y = object_coordinates[index_list[0]][1]        
        player = Player(player_x, player_y)
        win = Win(grid[0][9], grid[1][3])
        pause = Button(back_button, "", 30, WIDTH - 50, 50, SQUARE_LENGTH, SQUARE_LENGTH)

        level_group = pygame.sprite.Group()
        level_group.add(win, player, pause,
                        wall_factory([[x, 2] for x in range(0, 17)]), # Top wall barrier
                        wall_factory([[x, 6] for x in range(0, 17)]), # Bottom wall barrier
                        wall_factory([[0, y] for y in range(3, 6)]), # Left wall barrier
                        wall_factory([[15, y] for y in range(3, 6)]), # Rightwall barrier
                        wall_factory([[2, 4], [2, 5]]), # First rectangle barrier
                        wall_factory([[4, 3], [4, 4]]), # Second rectangle barrier
                        wall_factory([[6, 4], [6, 5]]), # Third rectangle barrier
                        wall_factory([[8, 3]]), # Singular barrier preventing from going to the goal
                        wall_factory([[x, 4] for x in range(8, 14)]) # Long barrier making journey to goal tedious
                        )
        
        index_list = []
        object_coordinates = [[]]
        
    # Go back to the pause menu and load the objects to the screen
    if reload_paused:

        # Fixes the flashing bug
        overlay.set_alpha(10)
        screen.blit(overlay, overlay_rect)

        index_list = [0]
        object_coordinates = [[player.rect.x, player.rect.y]]
        pause_menu(level_4)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.terminate()
            player.movement(event) # Check for the player movement
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if pause.rect.collidepoint(event.pos) and not player.moving:
                        game.garbage_disposal([level_group]) # Free up the memory
                        menu_forward.play()
                        index_list = [0] # Look at first index first
                        object_coordinates = [[player.rect.x, player.rect.y]] # Coordinates of all MOVING objects
                        pause_menu(level_4) # The game is paused

        if player.current_frame < player.target_frame: # If the player is not done moving...
            player.rect.y += player.dy # Update the y position
            player.rect.x += player.dx # Update the x position
            for wall in level_group: # For each wall in the group...
                if isinstance(wall, Wall): # Checks if the "wall" is a wall
                    wall.check_collision(player)
            player.current_frame += 1 # Increment the current frame

        if player.rect == win.rect:
            game.garbage_disposal([player, win, level_group])
            win_menu(level_4)
        
        # If the player has completed moving, then tell the game that they are no longer moving
        if player.current_frame >= player.target_frame:
            player.moving = False

        game.generate_background(background1)

        level_group.update()
        level_group.draw(screen)

        game.update_state()

def level_5(paused = False, reload_paused = False):
    """Level 5"""
    global index_list, object_coordinates

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA) # Overlays the level translucent
    overlay.fill((10, 10, 10)) # Grey
    overlay_rect = overlay.get_rect(topleft = (0, 0))

    # Load in all object in normal positions
    if not paused:

        player = Player(grid[0][4], grid[1][7])
        win = Win(grid[0][8], grid[1][5])
        pause = Button(back_button, "", 30, WIDTH - 50, 50, SQUARE_LENGTH, SQUARE_LENGTH)

        level_group = pygame.sprite.Group()
        level_group.add(win, player, pause,
                        wall_factory([[x, 8] for x in range(3, 13)]), # Bottom barrier
                        wall_factory([[x, 0] for x in range(3, 13)]), # Top barrier
                        wall_factory([[3, y] for y in range(1, 8)]), # Left barrier
                        wall_factory([[12, y] for y in range(1, 8)]), # Right barrier
                        wall_factory([[5, y] for y in range(2, 8)]), # First wall
                        wall_factory([[x, 2] for x in range(6, 11)]), # Second wall
                        wall_factory([[10, y] for y in range(2, 7)]), # Third wall
                        wall_factory([[x, 6] for x in range(8, 10)]), # Fourth wall
                        wall_factory([[7, y] for y in range(4, 7)]), # Fifth wall
                        wall_factory([[8, 4]]) # Final wall
                        )
        
        # Play a random sound 20% of the time
        if random.randint(0, 4) == 3: # CHANGE TO 3
            level_with_only_player_sounds_copy = sounds.level_with_only_player_sounds[:4] # Copy of list without the last voice line
            narrator = pygame.mixer.Sound(random.choice(level_with_only_player_sounds_copy)) # Random choice of voiceline
            narrator.set_volume(narrator_volume)
            narrator.play()
        
    # Load in objects at last known coordinates based upon the index list's preference
    elif paused:

        # Define player x and y positions, using index list to find right recursive array position
        player_x = object_coordinates[index_list[0]][0]
        player_y = object_coordinates[index_list[0]][1]        
        player = Player(player_x, player_y)
        win = Win(grid[0][8], grid[1][5])
        pause = Button(back_button, "", 30, WIDTH - 50, 50, SQUARE_LENGTH, SQUARE_LENGTH)

        level_group = pygame.sprite.Group()
        level_group.add(win, player, pause,
                        wall_factory([[x, 8] for x in range(3, 13)]), # Bottom barrier
                        wall_factory([[x, 0] for x in range(3, 13)]), # Top barrier
                        wall_factory([[3, y] for y in range(1, 8)]), # Left barrier
                        wall_factory([[12, y] for y in range(1, 8)]), # Right barrier
                        wall_factory([[5, y] for y in range(2, 8)]), # First wall
                        wall_factory([[x, 2] for x in range(6, 11)]), # Second wall
                        wall_factory([[10, y] for y in range(2, 7)]), # Third wall
                        wall_factory([[x, 6] for x in range(8, 10)]), # Fourth wall
                        wall_factory([[7, y] for y in range(4, 7)]), # Fifth wall
                        wall_factory([[8, 4]]) # Final wall
                        )
        
        index_list = []
        object_coordinates = [[]]
        
    # Go back to the pause menu and load the objects to the screen
    if reload_paused:

        # Fixes the flashing bug
        overlay.set_alpha(10)
        screen.blit(overlay, overlay_rect)

        index_list = [0]
        object_coordinates = [[player.rect.x, player.rect.y]]
        pause_menu(level_5)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.terminate()
            player.movement(event) # Check for the player movement
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if pause.rect.collidepoint(event.pos) and not player.moving:
                        game.garbage_disposal([level_group]) # Free up the memory
                        menu_forward.play()
                        index_list = [0] # Look at first index first
                        object_coordinates = [[player.rect.x, player.rect.y]] # Coordinates of all MOVING objects
                        pause_menu(level_5) # The game is paused

        if player.current_frame < player.target_frame: # If the player is not done moving...
            player.rect.y += player.dy # Update the y position
            player.rect.x += player.dx # Update the x position
            for wall in level_group: # For each wall in the group...
                if isinstance(wall, Wall): # Checks if the "wall" is a wall
                    wall.check_collision(player)
            player.current_frame += 1 # Increment the current frame

        if player.rect == win.rect:
            game.garbage_disposal([player, win, level_group])
            win_menu(level_5)
        
        # If the player has completed moving, then tell the game that they are no longer moving
        if player.current_frame >= player.target_frame:
            player.moving = False

        game.generate_background(background1)

        level_group.update()
        level_group.draw(screen)

        game.update_state()

def level_6(paused = False, reload_paused = False):
    """Level VI"""

    global index_list, object_coordinates

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA) # Overlays the level translucent
    overlay.fill((10, 10, 10)) # Grey
    overlay_rect = overlay.get_rect(topleft = (0, 0))

    # Load in all object in normal positions
    if not paused:

        player = Player(grid[0][5], grid[1][4])
        win = Win(grid[0][10], grid[1][4])
        pause = Button(back_button, "", 30, WIDTH - 50, 50, SQUARE_LENGTH, SQUARE_LENGTH)
        static1 = enemy.Enemy.Static(grid[0][9], grid[1][4])

        level_group = pygame.sprite.Group()
        level_group.add(static1, 
                        win, player, pause,
                        wall_factory([[x, 2] for x in range(4, 12)]), # Top barrier
                        wall_factory([[x, 5] for x in range(4, 12)]), # Bottom barrier
                        wall_factory([[4, y] for y in range(3, 5)]), # Left barrier
                        wall_factory([[11, y] for y in range(3, 5)]),) # Right barrier
        
        # Play a random sound 20% of the time
        if random.randint(0, 4) == 3: # CHANGE TO 3
            narrator = pygame.mixer.Sound(random.choice(sounds.level_containing_static_sounds)) # Random choice of voiceline
            narrator.set_volume(narrator_volume)
            narrator.play()
            
    # Load in objects at last known coordinates based upon the index list's preference
    elif paused:

        # Define player x and y positions, using index list to find right recursive array position
        player_x = object_coordinates[index_list[0]][0]
        player_y = object_coordinates[index_list[0]][1]
        
        player = Player(player_x, player_y)
        win = Win(grid[0][10], grid[1][4])
        pause = Button(back_button, "", 30, WIDTH - 50, 50, SQUARE_LENGTH, SQUARE_LENGTH)
        static1 = enemy.Enemy.Static(grid[0][9], grid[1][4])

        level_group = pygame.sprite.Group()
        level_group.add(static1, 
                        win, player, pause,
                        wall_factory([[x, 2] for x in range(4, 12)]),
                        wall_factory([[x, 5] for x in range(4, 12)]),
                        wall_factory([[4, y] for y in range(3, 5)]), 
                        wall_factory([[11, y] for y in range(3, 5)]),)
        
        index_list = []
        object_coordinates = [[]]
        
    # Go back to the pause menu and load the objects to the screen
    if reload_paused:
        #game.generate_background(background1)
        #level_group.draw(screen) <-- Bug

        # Fixes the flashing bug
        overlay.set_alpha(10)
        screen.blit(overlay, overlay_rect)

        index_list = [0]
        object_coordinates = [[player.rect.x, player.rect.y]]
        pause_menu(level_6)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.terminate()
            player.movement(event) # Check for the player movement
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if pause.rect.collidepoint(event.pos) and not player.moving:
                        game.garbage_disposal([level_group]) # Free up the memory
                        menu_forward.play()
                        index_list = [0] # Look at first index first
                        object_coordinates = [[player.rect.x, player.rect.y]] # Coordinates of all MOVING objects
                        pause_menu(level_6) # The game is paused

        if player.current_frame < player.target_frame: # If the player is not done moving...
            player.rect.y += player.dy # Update the y position
            player.rect.x += player.dx # Update the x position

            player.current_frame += 1 # Increment the current frame

            # CHECKING OBJECTS
            for object in level_group: # For each object in the group...
                if isinstance(object, Wall): # Checks if the "wall" is a wall
                    object.check_collision(player)

                # Check if the lose state condition is met 
                elif isinstance(object, enemy.Enemy.Static):
                    lose = object.check_collision(player)
                    if lose and not player.loss:
                        player.set_loss(lose)

        # Restart the level if the lose state has been fulfilled
        if not player.loss_animation and player.loss:
            player.loss = False
            level_6()

        # If the player wins, load the win menu
        if player.rect == win.rect:
            game.garbage_disposal([player, win, level_group])
            win_menu(level_6)
        
        # If the player has completed moving, then tell the game that they are no longer moving
        if player.current_frame >= player.target_frame:
            player.moving = False

        game.generate_background(background1)

        level_group.update()
        level_group.draw(screen)

        game.update_state()

def level_7(paused = False, reload_paused = False):
    """LEVEL 7"""

    global index_list, object_coordinates

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA) # Overlays the level translucent
    overlay.fill((10, 10, 10)) # Grey
    overlay_rect = overlay.get_rect(topleft = (0, 0))

    # Load in all object in normal positions
    if not paused:

        player = Player(grid[0][5], grid[1][3])
        win = Win(grid[0][11], grid[1][3])
        pause = Button(back_button, "", 30, WIDTH - 50, 50, SQUARE_LENGTH, SQUARE_LENGTH)

        level_group = pygame.sprite.Group()
        level_group.add(enemy.enemy_factory([[5, 6], [10, 4], [11, 4]], enemy.Enemy.Static), # Singular enemies
                        enemy.enemy_factory([[7, y] for y in range(3, 6)], enemy.Enemy.Static), # First wall
                        enemy.enemy_factory([[8, y] for y in range(3, 5)], enemy.Enemy.Static), # Second wall
                        win, player, pause,
                        wall_factory([[x, 2] for x in range(4, 13)]), # Top barrier
                        wall_factory([[x, 7] for x in range(4, 13)]), # Bottom barrier
                        wall_factory([[4, y] for y in range(3, 8)]), # Left barrier 
                        wall_factory([[12, y] for y in range(3, 8)]) # Right barrier
                        )

        # Play a random sound 20% of the time
        if random.randint(0, 4) == 3: # CHANGE TO 3
            narrator = pygame.mixer.Sound(random.choice(sounds.level_containing_static_sounds)) # Random choice of voiceline
            narrator.set_volume(narrator_volume)
            narrator.play()
    
    # Load in objects at last known coordinates based upon the index list's preference
    elif paused:

        # Define player x and y positions, using index list to find right recursive array position
        player_x = object_coordinates[index_list[0]][0]
        player_y = object_coordinates[index_list[0]][1]
        
        player = Player(player_x, player_y)
        win = Win(grid[0][11], grid[1][3])
        pause = Button(back_button, "", 30, WIDTH - 50, 50, SQUARE_LENGTH, SQUARE_LENGTH)
        static1 = enemy.Enemy.Static(grid[0][9], grid[1][4])

        level_group = pygame.sprite.Group()
        level_group.add(enemy.enemy_factory([[5, 6], [10, 4], [11, 4]], enemy.Enemy.Static), # Singular enemies
                        enemy.enemy_factory([[7, y] for y in range(3, 6)], enemy.Enemy.Static), # First wall
                        enemy.enemy_factory([[8, y] for y in range(3, 5)], enemy.Enemy.Static), # Second wall
                        win, player, pause,
                        wall_factory([[x, 2] for x in range(4, 13)]), # Top barrier
                        wall_factory([[x, 7] for x in range(4, 13)]), # Bottom barrier
                        wall_factory([[4, y] for y in range(3, 8)]), # Left barrier 
                        wall_factory([[12, y] for y in range(3, 8)]) # Right barrier
                        )
        
        index_list = []
        object_coordinates = [[]]
        
    # Go back to the pause menu and load the objects to the screen
    if reload_paused:
        # Fixes the flashing bug
        overlay.set_alpha(10)
        screen.blit(overlay, overlay_rect)

        index_list = [0]
        object_coordinates = [[player.rect.x, player.rect.y]]
        pause_menu(level_7)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.terminate()
            player.movement(event) # Check for the player movement
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if pause.rect.collidepoint(event.pos) and not player.moving:
                        game.garbage_disposal([level_group]) # Free up the memory
                        menu_forward.play()
                        index_list = [0] # Look at first index first
                        object_coordinates = [[player.rect.x, player.rect.y]] # Coordinates of all MOVING objects
                        pause_menu(level_7) # The game is paused

        if player.current_frame < player.target_frame: # If the player is not done moving...
            player.rect.y += player.dy # Update the y position
            player.rect.x += player.dx # Update the x position

            player.current_frame += 1 # Increment the current frame

            # CHECKING OBJECTS
            for object in level_group: # For each object in the group...
                if isinstance(object, Wall): # Checks if the "wall" is a wall
                    object.check_collision(player)

                # Check if the lose state condition is met 
                elif isinstance(object, enemy.Enemy.Static):
                    lose = object.check_collision(player)
                    if lose and not player.loss:
                        player.set_loss(lose)

        # Restart the level if the lose state has been fulfilled
        if not player.loss_animation and player.loss:
            player.loss = False
            level_7()

        # If the player wins, load the win menu
        if player.rect == win.rect:
            game.garbage_disposal([player, win, level_group])
            win_menu(level_7)
        
        # If the player has completed moving, then tell the game that they are no longer moving
        if player.current_frame >= player.target_frame:
            player.moving = False

        game.generate_background(background1)

        level_group.update()
        level_group.draw(screen)

        game.update_state()

def level_8(paused = False, reload_paused = False):
    """Level VIII"""
    global object_coordinates

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA) # Overlays the level translucent
    overlay.fill((10, 10, 10)) # Grey
    overlay_rect = overlay.get_rect(topleft = (0, 0))

    # Load in all object in normal positions
    if not paused:

        player = Player(grid[0][3], grid[1][5])
        win = Win(grid[0][14], grid[1][4])
        pause = Button(back_button, "", 30, WIDTH - 50, 50, SQUARE_LENGTH, SQUARE_LENGTH)
        dynamic1 = enemy.Enemy.Dynamic(grid[0][9], grid[1][4], style="seek")

        level_group = pygame.sprite.Group()
        level_group.add(dynamic1, win, player, pause,
                        # Barrier around level
                        wall_factory([[x, 0] for x in range(0, 16)]),
                        wall_factory([[x, 8] for x in range(0, 16)]),
                        wall_factory([[0, y] for y in range(0, 9)]),
                        wall_factory([[15, y] for y in range(0, 9)]),

                        # Barriers surrounding win
                        wall_factory([[x, 3] for x in range(12, 15)]),
                        wall_factory([[x, 5] for x in range(12, 15)])
                        )
        
        # Play a random sound 20% of the time
        if random.randint(0, 4) == 3: # CHANGE TO 3
            narrator = pygame.mixer.Sound(random.choice(sounds.level_containing_dynamic_sounds)) # Random choice of voiceline
            narrator.set_volume(narrator_volume)
            narrator.play()
    
    # Load in objects at last known coordinates based upon the index list's preference
    elif paused:
        
        # Update position of moving objects
        dynamic1_x, dynamic1_y = object_coordinates[0][0], object_coordinates[0][1]
        player_x, player_y = object_coordinates[1][0], object_coordinates[1][1]
        
        player = Player(player_x, player_y)
        win = Win(grid[0][14], grid[1][4])
        pause = Button(back_button, "", 30, WIDTH - 50, 50, SQUARE_LENGTH, SQUARE_LENGTH)
        dynamic1 = enemy.Enemy.Dynamic(dynamic1_x, dynamic1_y, style="seek")

        level_group = pygame.sprite.Group()
        level_group.add(dynamic1, win, player, pause,
                        # Barrier around level
                        wall_factory([[x, 0] for x in range(0, 16)]),
                        wall_factory([[x, 8] for x in range(0, 16)]),
                        wall_factory([[0, y] for y in range(0, 9)]),
                        wall_factory([[15, y] for y in range(0, 9)]),

                        # Barriers surrounding win
                        wall_factory([[x, 3] for x in range(12, 15)]),
                        wall_factory([[x, 5] for x in range(12, 15)])
                        )
        
        
        object_coordinates = list()
        
    # Go back to the pause menu and load the objects to the screen
    if reload_paused:

        # Fixes the flashing bug
        overlay.set_alpha(10)
        screen.blit(overlay, overlay_rect)
        
       # Storing co-ordinates of all moving objects
        # Storing co-ordinates of all moving objects
        for object in level_group:
            # If the object can move, get its coordinates
            if isinstance(object, enemy.Enemy.Dynamic) or isinstance(object, Player):
                # Rounding of coordinates
                if isinstance(object, enemy.Enemy.Dynamic):
                    print(object.rect.x, object.rect.y)
                    # If the coordinates fit within the tile spaces, add them to list)
                    if object.rect.x % SQUARE_LENGTH == 0 and object.rect.y % SQUARE_LENGTH == 0:
                        object_coordinates.append([object.rect.x, object.rect.y])

                    # Method if the above condition is not satisfied
                    else:
                        # Closest rounded coordinates relative to grid (so not multiple of 80)
                        nearest_x = round(object.rect.x / SQUARE_LENGTH)
                        nearest_y = round(object.rect.y / SQUARE_LENGTH)

                        # Lists of integers to hold the best two coordinates for each axis
                        choice_of_x = []
                        choice_of_y = []

                        # Based on how the number was rounded, determine the best pair of coordinates
                        # C1 < rounded_x < C2 where C1 and C2 are best pair of coordinates

                        if nearest_x > object.rect.x / SQUARE_LENGTH:
                            choice_of_x = [(nearest_x - 1) * 80, nearest_x * 80]

                        elif nearest_x < object.rect.x / SQUARE_LENGTH:
                            choice_of_x = [nearest_x * 80, (nearest_x + 1) * 80]
                        
                        # The case for if only one of the coordinates are a multiple of 80
                        else:
                            # 10000 as second best coordinate to ensure first coordinate is picked
                            choice_of_x = [nearest_x * 80, 10000]

                        if nearest_y < object.rect.y / SQUARE_LENGTH:
                            choice_of_y = [(nearest_y - 1) * 80, nearest_x * 80]

                        elif nearest_y > object.rect.y / SQUARE_LENGTH:
                            choice_of_y = [nearest_y * 80, (nearest_x + 1) * 80]

                        # The case for if only one of the coordinates are a multiple of 80
                        else:
                            # 10000 as second best coordinate to ensure first coordinate is picked
                            choice_of_y = [nearest_y * 80, 10000]

                        # Finds both distances between the object's position and the best choices of the coordinates
                        difference_x = [abs(object.rect.x - choice_of_x[0]), abs(object.rect.x - choice_of_x[1])]
                        difference_y = [abs(object.rect.y - choice_of_y[0]), abs(object.rect.y - choice_of_y[1])]

                        # Finds the index for the smallest distance
                        chosen_x = difference_x.index(min(difference_x))
                        chosen_y = difference_y.index(min(difference_y))

                        object_coordinates.append([choice_of_x[chosen_x], choice_of_y[chosen_y]])
                    
                else:
                    object_coordinates.append([object.rect.x, object.rect.y])

        pause_menu(level_8)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.terminate()
            player.movement(event) # Check for the player movement
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if pause.rect.collidepoint(event.pos) and not player.moving:
                        game.garbage_disposal([level_group]) # Free up the memory
                        menu_forward.play()

                        # Storing co-ordinates of all moving objects
                        for object in level_group:
                            # If the object can move, get its coordinates
                            if isinstance(object, enemy.Enemy.Dynamic) or isinstance(object, Player):
                                # Rounding of coordinates
                                if isinstance(object, enemy.Enemy.Dynamic):
                                    print(object.rect.x, object.rect.y)
                                    # If the coordinates fit within the tile spaces, add them to list)
                                    if object.rect.x % SQUARE_LENGTH == 0 and object.rect.y % SQUARE_LENGTH == 0:
                                        object_coordinates.append([object.rect.x, object.rect.y])

                                    # Method if the above condition is not satisfied
                                    else:
                                        # Closest rounded coordinates relative to grid (so not multiple of 80)
                                        nearest_x = round(object.rect.x / SQUARE_LENGTH)
                                        nearest_y = round(object.rect.y / SQUARE_LENGTH)

                                        # Lists of integers to hold the best two coordinates for each axis
                                        choice_of_x = []
                                        choice_of_y = []

                                        # Based on how the number was rounded, determine the best pair of coordinates
                                        # C1 < rounded_x < C2 where C1 and C2 are best pair of coordinates

                                        if nearest_x > object.rect.x / SQUARE_LENGTH:
                                            choice_of_x = [(nearest_x - 1) * 80, nearest_x * 80]

                                        elif nearest_x < object.rect.x / SQUARE_LENGTH:
                                            choice_of_x = [nearest_x * 80, (nearest_x + 1) * 80]
                                        
                                        # The case for if only one of the coordinates are a multiple of 80
                                        else:
                                            # 10000 as second best coordinate to ensure first coordinate is picked
                                            choice_of_x = [nearest_x * 80, 10000]

                                        if nearest_y < object.rect.y / SQUARE_LENGTH:
                                            choice_of_y = [(nearest_y - 1) * 80, nearest_x * 80]

                                        elif nearest_y > object.rect.y / SQUARE_LENGTH:
                                            choice_of_y = [nearest_y * 80, (nearest_x + 1) * 80]

                                        # The case for if only one of the coordinates are a multiple of 80
                                        else:
                                            # 10000 as second best coordinate to ensure first coordinate is picked
                                            choice_of_y = [nearest_y * 80, 10000]

                                        # Finds both distances between the object's position and the best choices of the coordinates
                                        difference_x = [abs(object.rect.x - choice_of_x[0]), abs(object.rect.x - choice_of_x[1])]
                                        difference_y = [abs(object.rect.y - choice_of_y[0]), abs(object.rect.y - choice_of_y[1])]

                                        # Finds the index for the smallest distance
                                        chosen_x = difference_x.index(min(difference_x))
                                        chosen_y = difference_y.index(min(difference_y))

                                        object_coordinates.append([choice_of_x[chosen_x], choice_of_y[chosen_y]])
                                    
                                else:
                                    object_coordinates.append([object.rect.x, object.rect.y])

                        pause_menu(level_8) # The game is paused

        if player.current_frame < player.target_frame: # If the player is not done moving...
            player.rect.y += player.dy # Update the y position
            player.rect.x += player.dx # Update the x position

            player.current_frame += 1 # Increment the current frame

        # CHECKING OBJECTS
        for object in level_group: # For each object in the group...
            if isinstance(object, Wall): # Checks if the "wall" is a wall
                for object_2 in level_group:
                    if isinstance(object_2, Player) or isinstance(object_2, enemy.Enemy.Dynamic):
                        object.check_collision(object_2)

            # Check if the lose state condition is met 
            if isinstance(object, enemy.Enemy.Static) or isinstance(object, enemy.Enemy.Dynamic):
                lose = object.check_collision(player)
                if lose and not player.loss:
                    player.set_loss(lose)

            # Gets the player's coordinates
            if isinstance(object, enemy.Enemy.Dynamic):
                if object.since_movement == object.target_movement_time - 1: # Frame before movement
                    object.get_player_position(player.rect)

        # Restart the level if the lose state has been fulfilled
        if not player.loss_animation and player.loss:
            player.loss = False
            level_8()

        # If the player wins, load the win menu
        if player.rect == win.rect:
            game.garbage_disposal([player, win, level_group])
            win_menu(level_8)
        
        # If the player has completed moving, then tell the game that they are no longer moving
        if player.current_frame >= player.target_frame:
            player.moving = False

        game.generate_background(background1)

        level_group.update()
        level_group.draw(screen)
        
        # Pause is not behind blocks
        pause.update()

        game.update_state()

def level_9(paused = False, reload_paused = False):
    """Level IX"""
    global object_coordinates

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA) # Overlays the level translucent
    overlay.fill((10, 10, 10)) # Grey
    overlay_rect = overlay.get_rect(topleft = (0, 0))

    # Load in all object in normal positions
    if not paused:

        player = Player(grid[0][1], grid[1][4])
        win = Win(grid[0][14], grid[1][4])
        pause = Button(back_button, "", 30, WIDTH - 50, 50, SQUARE_LENGTH, SQUARE_LENGTH)
        dynamic1 = enemy.Enemy.Dynamic(grid[0][11], grid[1][3], frequency=5, style="seek")
        dynamic2 = enemy.Enemy.Dynamic(grid[0][11], grid[1][5], frequency=4, delay=35, style="seek")
        dynamic3 = enemy.Enemy.Dynamic(grid[0][11], grid[1][4], frequency=3, delay=10, style="burst")

        level_group = pygame.sprite.Group()
        level_group.add(dynamic1, dynamic2, dynamic3,
                        win, player, pause,
                        # Barrier around level
                        wall_factory([[x, 0] for x in range(0, 16)]),
                        wall_factory([[x, 8] for x in range(0, 16)]),
                        wall_factory([[0, y] for y in range(0, 9)]),
                        wall_factory([[15, y] for y in range(0, 9)]),

                        # Barriers surrounding win
                        wall_factory([[x, 3] for x in range(12, 15)]),
                        wall_factory([[x, 5] for x in range(12, 15)])
                        )
        
        # Play a random sound 20% of the time
        if random.randint(0, 4) == 3: # CHANGE TO 3
            narrator = pygame.mixer.Sound(random.choice(sounds.level_containing_dynamic_sounds)) # Random choice of voiceline
            narrator.set_volume(narrator_volume)
            narrator.play()
    
    # Load in objects at last known coordinates based upon the index list's preference
    elif paused:
        
        # Update position of moving objects
        dynamic1_x, dynamic1_y = object_coordinates[0][0], object_coordinates[0][1]
        dynamic2_x, dynamic2_y = object_coordinates[1][0], object_coordinates[1][1]
        dynamic3_x, dynamic3_y = object_coordinates[2][0], object_coordinates[2][1]
        player_x, player_y = object_coordinates[3][0], object_coordinates[3][1]
        
        player = Player(player_x, player_y)
        win = Win(grid[0][14], grid[1][4])
        pause = Button(back_button, "", 30, WIDTH - 50, 50, SQUARE_LENGTH, SQUARE_LENGTH)
        dynamic1 = enemy.Enemy.Dynamic(dynamic1_x, dynamic1_y, frequency=5, style="seek")
        dynamic2 = enemy.Enemy.Dynamic(dynamic2_x, dynamic2_y, frequency=4, delay=35, style="seek")
        dynamic3 = enemy.Enemy.Dynamic(dynamic3_x, dynamic3_y, frequency=3, delay=10, style="burst")

        level_group = pygame.sprite.Group()
        level_group.add(dynamic1, dynamic2, dynamic3,
                        win, player, pause,
                        # Barrier around level
                        wall_factory([[x, 0] for x in range(0, 16)]),
                        wall_factory([[x, 8] for x in range(0, 16)]),
                        wall_factory([[0, y] for y in range(0, 9)]),
                        wall_factory([[15, y] for y in range(0, 9)]),

                        # Barriers surrounding win
                        wall_factory([[x, 3] for x in range(12, 15)]),
                        wall_factory([[x, 5] for x in range(12, 15)])
                        )
        
        
        object_coordinates = list()
        
    # Go back to the pause menu and load the objects to the screen
    if reload_paused:

        # Fixes the flashing bug
        overlay.set_alpha(10)
        screen.blit(overlay, overlay_rect)
        
       # Storing co-ordinates of all moving objects
        # Storing co-ordinates of all moving objects
        for object in level_group:
            # If the object can move, get its coordinates
            if isinstance(object, enemy.Enemy.Dynamic) or isinstance(object, Player):
                # Rounding of coordinates
                if isinstance(object, enemy.Enemy.Dynamic):
                    print(object.rect.x, object.rect.y)
                    # If the coordinates fit within the tile spaces, add them to list)
                    if object.rect.x % SQUARE_LENGTH == 0 and object.rect.y % SQUARE_LENGTH == 0:
                        object_coordinates.append([object.rect.x, object.rect.y])

                    # Method if the above condition is not satisfied
                    else:
                        # Closest rounded coordinates relative to grid (so not multiple of 80)
                        nearest_x = round(object.rect.x / SQUARE_LENGTH)
                        nearest_y = round(object.rect.y / SQUARE_LENGTH)

                        # Lists of integers to hold the best two coordinates for each axis
                        choice_of_x = []
                        choice_of_y = []

                        # Based on how the number was rounded, determine the best pair of coordinates
                        # C1 < rounded_x < C2 where C1 and C2 are best pair of coordinates

                        if nearest_x > object.rect.x / SQUARE_LENGTH:
                            choice_of_x = [(nearest_x - 1) * 80, nearest_x * 80]

                        elif nearest_x < object.rect.x / SQUARE_LENGTH:
                            choice_of_x = [nearest_x * 80, (nearest_x + 1) * 80]
                        
                        # The case for if only one of the coordinates are a multiple of 80
                        else:
                            # 10000 as second best coordinate to ensure first coordinate is picked
                            choice_of_x = [nearest_x * 80, 10000]

                        if nearest_y < object.rect.y / SQUARE_LENGTH:
                            choice_of_y = [(nearest_y - 1) * 80, nearest_x * 80]

                        elif nearest_y > object.rect.y / SQUARE_LENGTH:
                            choice_of_y = [nearest_y * 80, (nearest_x + 1) * 80]

                        # The case for if only one of the coordinates are a multiple of 80
                        else:
                            # 10000 as second best coordinate to ensure first coordinate is picked
                            choice_of_y = [nearest_y * 80, 10000]

                        # Finds both distances between the object's position and the best choices of the coordinates
                        difference_x = [abs(object.rect.x - choice_of_x[0]), abs(object.rect.x - choice_of_x[1])]
                        difference_y = [abs(object.rect.y - choice_of_y[0]), abs(object.rect.y - choice_of_y[1])]

                        # Finds the index for the smallest distance
                        chosen_x = difference_x.index(min(difference_x))
                        chosen_y = difference_y.index(min(difference_y))

                        object_coordinates.append([choice_of_x[chosen_x], choice_of_y[chosen_y]])
                    
                else:
                    object_coordinates.append([object.rect.x, object.rect.y])

        pause_menu(level_9)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.terminate()
            player.movement(event) # Check for the player movement
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if pause.rect.collidepoint(event.pos) and not player.moving:
                        game.garbage_disposal([level_group]) # Free up the memory
                        menu_forward.play()

                        # Storing co-ordinates of all moving objects
                        for object in level_group:
                            # If the object can move, get its coordinates
                            if isinstance(object, enemy.Enemy.Dynamic) or isinstance(object, Player):
                                # Rounding of coordinates
                                if isinstance(object, enemy.Enemy.Dynamic):
                                    print(object.rect.x, object.rect.y)
                                    # If the coordinates fit within the tile spaces, add them to list)
                                    if object.rect.x % SQUARE_LENGTH == 0 and object.rect.y % SQUARE_LENGTH == 0:
                                        object_coordinates.append([object.rect.x, object.rect.y])

                                    # Method if the above condition is not satisfied
                                    else:
                                        # Closest rounded coordinates relative to grid (so not multiple of 80)
                                        nearest_x = round(object.rect.x / SQUARE_LENGTH)
                                        nearest_y = round(object.rect.y / SQUARE_LENGTH)

                                        # Lists of integers to hold the best two coordinates for each axis
                                        choice_of_x = []
                                        choice_of_y = []

                                        # Based on how the number was rounded, determine the best pair of coordinates
                                        # C1 < rounded_x < C2 where C1 and C2 are best pair of coordinates

                                        if nearest_x > object.rect.x / SQUARE_LENGTH:
                                            choice_of_x = [(nearest_x - 1) * 80, nearest_x * 80]

                                        elif nearest_x < object.rect.x / SQUARE_LENGTH:
                                            choice_of_x = [nearest_x * 80, (nearest_x + 1) * 80]
                                        
                                        # The case for if only one of the coordinates are a multiple of 80
                                        else:
                                            # 10000 as second best coordinate to ensure first coordinate is picked
                                            choice_of_x = [nearest_x * 80, 10000]

                                        if nearest_y < object.rect.y / SQUARE_LENGTH:
                                            choice_of_y = [(nearest_y - 1) * 80, nearest_x * 80]

                                        elif nearest_y > object.rect.y / SQUARE_LENGTH:
                                            choice_of_y = [nearest_y * 80, (nearest_x + 1) * 80]

                                        # The case for if only one of the coordinates are a multiple of 80
                                        else:
                                            # 10000 as second best coordinate to ensure first coordinate is picked
                                            choice_of_y = [nearest_y * 80, 10000]

                                        # Finds both distances between the object's position and the best choices of the coordinates
                                        difference_x = [abs(object.rect.x - choice_of_x[0]), abs(object.rect.x - choice_of_x[1])]
                                        difference_y = [abs(object.rect.y - choice_of_y[0]), abs(object.rect.y - choice_of_y[1])]

                                        # Finds the index for the smallest distance
                                        chosen_x = difference_x.index(min(difference_x))
                                        chosen_y = difference_y.index(min(difference_y))

                                        object_coordinates.append([choice_of_x[chosen_x], choice_of_y[chosen_y]])
                                    
                                else:
                                    object_coordinates.append([object.rect.x, object.rect.y])

                        pause_menu(level_9) # The game is paused

        if player.current_frame < player.target_frame: # If the player is not done moving...
            player.rect.y += player.dy # Update the y position
            player.rect.x += player.dx # Update the x position

            player.current_frame += 1 # Increment the current frame

        # CHECKING OBJECTS
        for object in level_group: # For each object in the group...
            if isinstance(object, Wall): # Checks if the "wall" is a wall
                for object_2 in level_group:
                    if isinstance(object_2, Player) or isinstance(object_2, enemy.Enemy.Dynamic):
                        object.check_collision(object_2)

            # Check if the lose state condition is met 
            if isinstance(object, enemy.Enemy.Static) or isinstance(object, enemy.Enemy.Dynamic):
                lose = object.check_collision(player)
                if lose and not player.loss:
                    player.set_loss(lose)

            # Gets the player's coordinates
            if isinstance(object, enemy.Enemy.Dynamic):
                if object.since_movement == object.target_movement_time - 1: # Frame before movement
                    object.get_player_position(player.rect)

        # Restart the level if the lose state has been fulfilled
        if not player.loss_animation and player.loss:
            player.loss = False
            level_9()

        # If the player wins, load the win menu
        if player.rect == win.rect:
            game.garbage_disposal([player, win, level_group])
            win_menu(level_9)
        
        # If the player has completed moving, then tell the game that they are no longer moving
        if player.current_frame >= player.target_frame:
            player.moving = False

        game.generate_background(background1)

        level_group.update()
        level_group.draw(screen)
        
        # Pause is not behind blocks
        pause.update()

        game.update_state()

def level_10(paused = False, reload_paused = False):
    """Level X"""
    global object_coordinates

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA) # Overlays the level translucent
    overlay.fill((10, 10, 10)) # Grey
    overlay_rect = overlay.get_rect(topleft = (0, 0))

    # Load in all object in normal positions
    if not paused:

        player = Player(grid[0][14], grid[1][4])
        win = Win(grid[0][1], grid[1][4])
        pause = Button(back_button, "", 30, WIDTH - 50, 50, SQUARE_LENGTH, SQUARE_LENGTH)
        dynamic1 = enemy.Enemy.Dynamic(grid[0][8], grid[1][4], frequency=4, style="burst")
        dynamic2 = enemy.Enemy.Dynamic(grid[0][5], grid[1][2], frequency=8, style="axisbound")
        dynamic3 = enemy.Enemy.Dynamic(grid[0][2], grid[1][4], frequency=5, style="seek")
        dynamic4 = enemy.Enemy.Dynamic(grid[0][5], grid[1][7], frequency=5, delay=15, style="axisbound")

        level_group = pygame.sprite.Group()
        level_group.add(dynamic1, dynamic2, dynamic3, dynamic4,
                        win, player, pause,
                        # Barrier around level
                        wall_factory([[x, 0] for x in range(0, 16)]),
                        wall_factory([[x, 8] for x in range(0, 16)]),
                        wall_factory([[0, y] for y in range(0, 9)]),
                        wall_factory([[15, y] for y in range(0, 9)]),

                        # Barriers surrounding win
                        wall_factory([[1, 3], [1, 5]]),

                        # Wall guarding the win
                        wall_factory([[4, y] for y in range(3, 6)]),
                        wall_factory([[4, 1], [4, 7]])
                        )
        
        # Play a random sound 20% of the time
        if random.randint(0, 4) == 3: # CHANGE TO 3
            narrator = pygame.mixer.Sound(random.choice(sounds.level_containing_dynamic_sounds)) # Random choice of voiceline
            narrator.set_volume(narrator_volume)
            narrator.play()
    
    # Load in objects at last known coordinates based upon the index list's preference
    elif paused:
        
        # Update position of moving objects
        dynamic1_x, dynamic1_y = object_coordinates[0][0], object_coordinates[0][1]
        dynamic2_x, dynamic2_y = object_coordinates[1][0], object_coordinates[1][1]
        dynamic3_x, dynamic3_y = object_coordinates[2][0], object_coordinates[2][1]
        dynamic4_x, dynamic4_y = object_coordinates[3][0], object_coordinates[3][1]
        player_x, player_y = object_coordinates[4][0], object_coordinates[4][1]
        
        player = Player(player_x, player_y)
        win = Win(grid[0][1], grid[1][4])
        pause = Button(back_button, "", 30, WIDTH - 50, 50, SQUARE_LENGTH, SQUARE_LENGTH)
        dynamic1 = enemy.Enemy.Dynamic(dynamic1_x, dynamic1_y, style="seek")
        dynamic2 = enemy.Enemy.Dynamic(dynamic2_x, dynamic2_y, frequency=8, style="axisbound")
        dynamic3 = enemy.Enemy.Dynamic(dynamic3_x, dynamic3_y, frequency=5, style="seek")
        dynamic4 = enemy.Enemy.Dynamic(dynamic4_x, dynamic4_y, frequency=5, delay=15, style="axisbound")

        level_group = pygame.sprite.Group()
        level_group.add(dynamic1, dynamic2, dynamic3, dynamic4,
                        win, player, pause,
                        # Barrier around level
                        wall_factory([[x, 0] for x in range(0, 16)]),
                        wall_factory([[x, 8] for x in range(0, 16)]),
                        wall_factory([[0, y] for y in range(0, 9)]),
                        wall_factory([[15, y] for y in range(0, 9)]),

                        # Barriers surrounding win
                        wall_factory([[1, 3], [1, 5]]),

                        # Wall guarding the win
                        wall_factory([[4, y] for y in range(3, 6)]),
                        wall_factory([[4, 1], [4, 7]])
                        )
        
        
        object_coordinates = list()
        
    # Go back to the pause menu and load the objects to the screen
    if reload_paused:

        # Fixes the flashing bug
        overlay.set_alpha(10)
        screen.blit(overlay, overlay_rect)
        
       # Storing co-ordinates of all moving objects
        # Storing co-ordinates of all moving objects
        for object in level_group:
            # If the object can move, get its coordinates
            if isinstance(object, enemy.Enemy.Dynamic) or isinstance(object, Player):
                # Rounding of coordinates
                if isinstance(object, enemy.Enemy.Dynamic):
                    # If the coordinates fit within the tile spaces, add them to list)
                    if object.rect.x % SQUARE_LENGTH == 0 and object.rect.y % SQUARE_LENGTH == 0:
                        object_coordinates.append([object.rect.x, object.rect.y])

                    # Method if the above condition is not satisfied
                    else:
                        # Closest rounded coordinates relative to grid (so not multiple of 80)
                        nearest_x = round(object.rect.x / SQUARE_LENGTH)
                        nearest_y = round(object.rect.y / SQUARE_LENGTH)

                        # Lists of integers to hold the best two coordinates for each axis
                        choice_of_x = []
                        choice_of_y = []

                        # Based on how the number was rounded, determine the best pair of coordinates
                        # C1 < rounded_x < C2 where C1 and C2 are best pair of coordinates

                        if nearest_x > object.rect.x / SQUARE_LENGTH:
                            choice_of_x = [(nearest_x - 1) * 80, nearest_x * 80]

                        elif nearest_x < object.rect.x / SQUARE_LENGTH:
                            choice_of_x = [nearest_x * 80, (nearest_x + 1) * 80]
                        
                        # The case for if only one of the coordinates are a multiple of 80
                        else:
                            # 10000 as second best coordinate to ensure first coordinate is picked
                            choice_of_x = [nearest_x * 80, 10000]

                        if nearest_y < object.rect.y / SQUARE_LENGTH:
                            choice_of_y = [(nearest_y - 1) * 80, nearest_x * 80]

                        elif nearest_y > object.rect.y / SQUARE_LENGTH:
                            choice_of_y = [nearest_y * 80, (nearest_x + 1) * 80]

                        # The case for if only one of the coordinates are a multiple of 80
                        else:
                            # 10000 as second best coordinate to ensure first coordinate is picked
                            choice_of_y = [nearest_y * 80, 10000]

                        # Finds both distances between the object's position and the best choices of the coordinates
                        difference_x = [abs(object.rect.x - choice_of_x[0]), abs(object.rect.x - choice_of_x[1])]
                        difference_y = [abs(object.rect.y - choice_of_y[0]), abs(object.rect.y - choice_of_y[1])]

                        # Finds the index for the smallest distance
                        chosen_x = difference_x.index(min(difference_x))
                        chosen_y = difference_y.index(min(difference_y))

                        object_coordinates.append([choice_of_x[chosen_x], choice_of_y[chosen_y]])
                    
                else:
                    object_coordinates.append([object.rect.x, object.rect.y])

        pause_menu(level_10)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.terminate()
            player.movement(event) # Check for the player movement
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if pause.rect.collidepoint(event.pos) and not player.moving:
                        game.garbage_disposal([level_group]) # Free up the memory
                        menu_forward.play()

                        # Storing co-ordinates of all moving objects
                        for object in level_group:
                            # If the object can move, get its coordinates
                            if isinstance(object, enemy.Enemy.Dynamic) or isinstance(object, Player):
                                # Rounding of coordinates
                                if isinstance(object, enemy.Enemy.Dynamic):
                                    print(object.rect.x, object.rect.y)
                                    # If the coordinates fit within the tile spaces, add them to list)
                                    if object.rect.x % SQUARE_LENGTH == 0 and object.rect.y % SQUARE_LENGTH == 0:
                                        object_coordinates.append([object.rect.x, object.rect.y])

                                    # Method if the above condition is not satisfied
                                    else:
                                        # Closest rounded coordinates relative to grid (so not multiple of 80)
                                        nearest_x = round(object.rect.x / SQUARE_LENGTH)
                                        nearest_y = round(object.rect.y / SQUARE_LENGTH)

                                        # Lists of integers to hold the best two coordinates for each axis
                                        choice_of_x = []
                                        choice_of_y = []

                                        # Based on how the number was rounded, determine the best pair of coordinates
                                        # C1 < rounded_x < C2 where C1 and C2 are best pair of coordinates

                                        if nearest_x > object.rect.x / SQUARE_LENGTH:
                                            choice_of_x = [(nearest_x - 1) * 80, nearest_x * 80]

                                        elif nearest_x < object.rect.x / SQUARE_LENGTH:
                                            choice_of_x = [nearest_x * 80, (nearest_x + 1) * 80]
                                        
                                        # The case for if only one of the coordinates are a multiple of 80
                                        else:
                                            # 10000 as second best coordinate to ensure first coordinate is picked
                                            choice_of_x = [nearest_x * 80, 10000]

                                        if nearest_y < object.rect.y / SQUARE_LENGTH:
                                            choice_of_y = [(nearest_y - 1) * 80, nearest_x * 80]

                                        elif nearest_y > object.rect.y / SQUARE_LENGTH:
                                            choice_of_y = [nearest_y * 80, (nearest_x + 1) * 80]

                                        # The case for if only one of the coordinates are a multiple of 80
                                        else:
                                            # 10000 as second best coordinate to ensure first coordinate is picked
                                            choice_of_y = [nearest_y * 80, 10000]

                                        # Finds both distances between the object's position and the best choices of the coordinates
                                        difference_x = [abs(object.rect.x - choice_of_x[0]), abs(object.rect.x - choice_of_x[1])]
                                        difference_y = [abs(object.rect.y - choice_of_y[0]), abs(object.rect.y - choice_of_y[1])]

                                        # Finds the index for the smallest distance
                                        chosen_x = difference_x.index(min(difference_x))
                                        chosen_y = difference_y.index(min(difference_y))

                                        object_coordinates.append([choice_of_x[chosen_x], choice_of_y[chosen_y]])
                                    
                                else:
                                    object_coordinates.append([object.rect.x, object.rect.y])

                        pause_menu(level_10) # The game is paused

        if player.current_frame < player.target_frame: # If the player is not done moving...
            player.rect.y += player.dy # Update the y position
            player.rect.x += player.dx # Update the x position

            player.current_frame += 1 # Increment the current frame

        # CHECKING OBJECTS
        for object in level_group: # For each object in the group...
            if isinstance(object, Wall): # Checks if the "wall" is a wall
                for object_2 in level_group:
                    if isinstance(object_2, Player) or isinstance(object_2, enemy.Enemy.Dynamic):
                        object.check_collision(object_2)

            # Check if the lose state condition is met 
            if isinstance(object, enemy.Enemy.Static) or isinstance(object, enemy.Enemy.Dynamic):
                lose = object.check_collision(player)
                if lose and not player.loss:
                    player.set_loss(lose)

            # Gets the player's coordinates
            if isinstance(object, enemy.Enemy.Dynamic):
                if object.since_movement == object.target_movement_time - 1: # Frame before movement
                    object.get_player_position(player.rect)

        # Restart the level if the lose state has been fulfilled
        if not player.loss_animation and player.loss:
            player.loss = False
            level_10()

        # If the player wins, load the win menu
        if player.rect == win.rect:
            game.garbage_disposal([player, win, level_group])
            win_menu(level_10)
        
        # If the player has completed moving, then tell the game that they are no longer moving
        if player.current_frame >= player.target_frame:
            player.moving = False

        game.generate_background(background1)

        level_group.update()
        level_group.draw(screen)
        
        # Pause is not behind blocks
        pause.update()

        game.update_state()

# ----------------------------------------------------------------------- #

# Setup for the screen/window
WIDTH = 1280
HEIGHT = 720
screen =  pygame.display.set_mode((WIDTH, HEIGHT)) # Dimensions = (1280, 720)
pygame.display.set_caption("Logical Psycho") # Sets the caption of the window
clock = pygame.time.Clock() # Creates a clock object to set frame rate
FPS = 60 # Frames per second5

# Setup for the tiles
SQUARE_LENGTH = 80 # Length of each edge of the tile
grid = [[x for x in range(0, WIDTH, SQUARE_LENGTH)], [y for y in range(0, HEIGHT, SQUARE_LENGTH)]] # Coordinate map for each tile

# Setup for images
background1 = join("Assets", "Block", "Background1.png") # Encapsulated path
background2 = join("Assets", "Block", "Background2.png")
background3 = join("Assets", "Block", "Background3.png")
background4 = join("Assets", "Block", "Background4.png")
background5 = join("Assets", "Block", "Background5.png")
background6 = join("Assets", "Block", "Background6.png")
block = join("Assets", "Block", "Block.png")

# Setup for sounds
narrator_volume = 0.5 # Variable to hold volume of sound between 0 and 1
sound_volume = 0.5

# JUST SOUNDS
menu_backward = pygame.mixer.Sound(sounds.effect_sounds[0])
menu_backward.set_volume(sound_volume)

menu_forward = pygame.mixer.Sound(sounds.effect_sounds[1])
menu_forward.set_volume(sound_volume)

level_select = pygame.mixer.Sound(sounds.effect_sounds[2])
level_select.set_volume(sound_volume)

lose_sound = pygame.mixer.Sound(sounds.effect_sounds[3])
lose_sound.set_volume(sound_volume * 0.5) # Quite loud

player_move_sound = pygame.mixer.Sound(sounds.effect_sounds[4])
player_move_sound.set_volume(sound_volume)

win_sound = pygame.mixer.Sound(sounds.effect_sounds[5])
win_sound.set_volume(sound_volume)

dynamic_sound = pygame.mixer.Sound(sounds.effect_sounds[6])
dynamic_sound.set_volume(sound_volume)

sound_list = [menu_backward, menu_forward, level_select, lose_sound, player_move_sound, win_sound, dynamic_sound, dynamic_sound]

# NARRATOR SOUNDS
main_menu_first = pygame.mixer.Sound(random.choice(sounds.main_menu_sounds)) # Sound object to play a sound from a path
main_menu_first.set_volume(narrator_volume) # Sets the volume of the sound relative to its original sound

main_menu_not_first = pygame.mixer.Sound(random.choice(sounds.main_menu_return_sounds))
main_menu_not_first.set_volume(narrator_volume)

win_menu_sound = pygame.mixer.Sound(random.choice(sounds.win_state_sounds))
win_menu_sound.set_volume(narrator_volume)

lose_narrator_sound = pygame.mixer.Sound(random.choice(sounds.lose_state_sounds))
lose_narrator_sound.set_volume(narrator_volume)

narrator_sound_list = [main_menu_first, main_menu_not_first, win_menu_sound, lose_sound]

# Setup for main menu

main_menu_visit_count = 0

text_1 = Text("Logical Psycho", WIDTH//2, HEIGHT//7, 50)

button_image = join("Assets", "Buttons", "Playbutton.png") # Path to the button image

play_button = Button(button_image, "PLAY", 50, WIDTH //2, HEIGHT//2.25, SQUARE_LENGTH * 4, SQUARE_LENGTH * 1.5) # Button object with arguemnts
settings_button = Button(button_image, "SETTINGS", 30, WIDTH //2, HEIGHT // 2.25 + 135, SQUARE_LENGTH * 4, SQUARE_LENGTH * 1.5)
quit_button = Button(button_image, "QUIT", 50, WIDTH // 2 , HEIGHT // 2.25 + 270, SQUARE_LENGTH * 4, SQUARE_LENGTH * 1.5)

button_group = pygame.sprite.Group() # Group object
button_group.add(play_button, settings_button, quit_button) # Adds button object to group | Group object acts as a list for Sprite objects

# Setup for settings menu
volume_button = join("Assets", "Buttons", "volumebutton.png")
back_button = join("Assets", "Buttons", "backbutton.png")

settings_title = Text("Settings", WIDTH//2, HEIGHT//9, 50)
narrator_volume_text = Text("Narrator Volume", WIDTH//5, HEIGHT//2.75, 30)
sound_volume_text = Text("Sound Volume", WIDTH//5, HEIGHT//2.75 + 150, 30)
delete_save_text = Text("Delete Save", WIDTH//5, HEIGHT//2.75 + 300, 30)

narrator_ui_volume = str(round(narrator_volume * 200)) # 0.5 in program = 100 in game
sound_ui_volume = str(round(sound_volume * 200))

narrator_volume_number = Text(narrator_ui_volume, WIDTH//2.25, HEIGHT//2.75, 30)
sound_volume_number = Text(sound_ui_volume, WIDTH//2.25, HEIGHT//2.75 + 150, 30)

button_to_hold_narrator_volume = Button(button_image, "", 50, WIDTH // 1.35, HEIGHT // 2.75, 600, SQUARE_LENGTH * 1.5)
button_to_hold_sound_volume = Button(button_image, "", 50, WIDTH // 1.35, HEIGHT // 2.75 + 150, 600, SQUARE_LENGTH * 1.5)

narrator_volume_scroller = Button(volume_button, "", 50, 1200, HEIGHT//2.75, SQUARE_LENGTH, SQUARE_LENGTH * 1.5) # 697 = most left, 1200 = most right
sound_volume_scroller = Button(volume_button, "", 50, 1200, HEIGHT//2.75 + 150, SQUARE_LENGTH, SQUARE_LENGTH * 1.5)

delete_save_button = Button(volume_button, "YES", 30, WIDTH//1.35, HEIGHT//2.75 + 300, SQUARE_LENGTH * 2.25, SQUARE_LENGTH * 2, BLACK)

go_back_button =  Button(back_button, "", 30, WIDTH - 50, 50, SQUARE_LENGTH, SQUARE_LENGTH)

settings_button_group = pygame.sprite.Group()
settings_button_group.add(button_to_hold_narrator_volume, button_to_hold_sound_volume, 
                          narrator_volume_scroller, sound_volume_scroller,
                          delete_save_button, go_back_button)

# Setup for 'confirm data deletion' menu
#warning_string = "                 Are you sure you want to\n       delete your progress?\n       Doing so will remove any futile \nefforts you made in this playthrough."
warning_string_replacement = "PRESS 'YES' TO DELETE DATA."
warning_text = Text(warning_string_replacement, WIDTH//2, HEIGHT//4, 40)
yes_button = Button(volume_button, "YES", 30, 500, HEIGHT - 200, SQUARE_LENGTH * 2.25, SQUARE_LENGTH * 2, BLACK)
no_button = Button(volume_button, "NO", 30, WIDTH - 500, HEIGHT - 200, SQUARE_LENGTH * 2.25, SQUARE_LENGTH * 2, BLACK)

data_deletion_group = pygame.sprite.Group()
data_deletion_group.add(yes_button, no_button)

# Setup for level selection menu
level_selection_title =  Text("Level Selection", WIDTH//2, HEIGHT//9, 50)

go_back_button_2 = Button(back_button, "", 30, WIDTH - 50, 50, SQUARE_LENGTH, SQUARE_LENGTH)

level_1_button = Level("01", grid[0][4], grid[1][4], level_1, False)
level_2_button = Level("02", grid[0][6], grid[1][4], level_2, False)
level_3_button = Level("03", grid[0][8], grid[1][4], level_3, False)
level_4_button = Level("04", grid[0][10], grid[1][4], level_4, False)
level_5_button = Level("05", grid[0][12], grid[1][4], level_5, False)
level_6_button = Level("06", grid[0][4], grid[1][6], level_6, False)
level_7_button = Level("07", grid[0][6], grid[1][6], level_7, False)
level_8_button = Level("08", grid[0][8], grid[1][6], level_8, False)
level_9_button = Level("09", grid[0][10], grid[1][6], level_9, False)
level_10_button = Level("10", grid[0][12], grid[1][6], level_10, False)


list_of_levels = [level_1_button, level_2_button, level_3_button, level_4_button, level_5_button,
                  level_6_button, level_7_button, level_8_button, level_9_button, level_10_button] # List of all levels

level_selection_button_group = pygame.sprite.Group()
level_selection_button_group.add(go_back_button_2,
                                 level_1_button, level_2_button, level_3_button, level_4_button, level_5_button,
                                 level_6_button, level_7_button, level_8_button, level_9_button, level_10_button)

# Setup for win menu

offset = 5 # Offset for the shadow of the text

win_title_background_image = join("Assets", "Block", "circularbackground.png") # Our circular background for the text

win_title = Text("Level Complete", WIDTH//2, HEIGHT//9, 40)
win_shadow = Text("Level Complete", WIDTH//2 + offset, HEIGHT//9 + offset, 40, BLACK) # The shadow is black and is below and to the right of the text
win_background = Button(win_title_background_image, "", 1, WIDTH//2, HEIGHT//9, SQUARE_LENGTH * 12, SQUARE_LENGTH * 1.75)

next_level_button = Button(button_image, "NEXT LEVEL", 30, 400, HEIGHT - 100, SQUARE_LENGTH * 5, SQUARE_LENGTH * 1.5)
go_back_to_levels_button = Button(button_image, "BACK TO LEVEL SELECTION", 15, WIDTH - 400, HEIGHT - 100, SQUARE_LENGTH * 5, SQUARE_LENGTH * 1.5)

win_buttons = pygame.sprite.Group()
win_buttons.add(next_level_button, go_back_to_levels_button, win_background)

# Setup for pause menu
index_list = [] # Stores the indexes we need to access in order to load moving objects into level
object_coordinates = [] # Stores the coordinates of each moving object

pause_title = Text("Paused", WIDTH//2, HEIGHT//9, 50)

resume_button = Button(button_image, "RESUME", 30, WIDTH //2, HEIGHT//2.25, SQUARE_LENGTH * 4, SQUARE_LENGTH * 1.5)
settings_button = Button(button_image, "SETTINGS", 30, WIDTH //2, HEIGHT // 2.25 + 135, SQUARE_LENGTH * 4, SQUARE_LENGTH * 1.5)
to_level_select_button = Button(button_image, "GO BACK", 30, WIDTH // 2 , HEIGHT // 2.25 + 270, SQUARE_LENGTH * 4, SQUARE_LENGTH * 1.5)

pause_group = pygame.sprite.Group()
pause_group.add(resume_button, settings_button, to_level_select_button)
          
# Menus
def main_menu():
    """Main menu that the user will load up."""
    global main_menu_visit_count
    
    # Play a different narrator sound if the user visits the menu too many times
    if main_menu_visit_count <= 2:
        if random.randint(1, 5) == 4:
            main_menu_first = pygame.mixer.Sound(random.choice(sounds.main_menu_sounds))
            main_menu_first.set_volume(narrator_volume)
            main_menu_first.play()
    
    else:
        if random.randint(1, 5) == 4:
            main_menu_not_first = pygame.mixer.Sound(random.choice(sounds.main_menu_return_sounds))
            main_menu_not_first.set_volume(narrator_volume)
            main_menu_not_first.play()

    main_menu_visit_count += 1
    
    load_data_from_game_file() # Loads data
    update_sounds(file="volume.txt", mode="read", volume1=narrator_volume, volume2=sound_volume) # Updates sounds

    # Updates volume
    sounds.change_volume(sound_list, sound_volume)
    sounds.change_volume(narrator_sound_list, narrator_volume)

    
    while True:
        for event in pygame.event.get(): # For each event that can happen...
            if event.type == pygame.QUIT: # If the user presses 'X' on the top left of the screen...
                menu_backward.play()
                game.terminate() # Quits the game
            if event.type == pygame.MOUSEBUTTONDOWN: # If the user presses the mouse button...
                if event.button == 1: # If the user presses the LEFT mouse button...
                    if quit_button.rect.collidepoint(event.pos): # If the mouse presses the quit button...
                        game.garbage_disposal([text_1, button_group]) # Free memory
                        game.terminate() # Quits the game
                    if settings_button.rect.collidepoint(event.pos): # If the mouse presses the settings button...
                        game.garbage_disposal([text_1, button_group]) # Free memory
                        menu_forward.play()
                        settings_menu() # Navigate to the settings menu
                    if play_button.rect.collidepoint(event.pos): # If the mouse presses the play button...
                        game.garbage_disposal([text_1, button_group]) # Free memory
                        menu_forward.play()
                        level_selection() # Navigate to the level selection menu

        game.generate_background(background5) # Generates the background

        text_1.update() # Displays text
        button_group.update() # Updates all the buttons

        game.update_state() # Updates the game window

def settings_menu(return_menu = main_menu):
    """Settings menu so the user can change features of the game."""
    global narrator_volume, sound_volume
    global narrator_volume_number, sound_volume_number
    global narrator_ui_volume, sound_ui_volume

    LOWERBOUND = 658
    UPPERBOUND = 1168
    RANGE = UPPERBOUND - LOWERBOUND # 1168 - 658 = 510

    narrator_moving = False
    sound_moving = False

    # REDEFINE IT ALL
    volume_button = join("Assets", "Buttons", "volumebutton.png")
    back_button = join("Assets", "Buttons", "backbutton.png")

    settings_title = Text("Settings", WIDTH//2, HEIGHT//9, 50)
    narrator_volume_text = Text("Narrator Volume", WIDTH//5, HEIGHT//2.75, 30)
    sound_volume_text = Text("Sound Volume", WIDTH//5, HEIGHT//2.75 + 150, 30)
    delete_save_text = Text("Delete Save", WIDTH//5, HEIGHT//2.75 + 300, 30)

    narrator_ui_volume = str(round(narrator_volume * 200)) # 0.5 in program = 100 in game
    sound_ui_volume = str(round(sound_volume * 200))

    narrator_volume_number = Text(narrator_ui_volume, WIDTH//2.25, HEIGHT//2.75, 30)
    sound_volume_number = Text(sound_ui_volume, WIDTH//2.25, HEIGHT//2.75 + 150, 30)

    button_to_hold_narrator_volume = Button(button_image, "", 50, WIDTH // 1.35, HEIGHT // 2.75, 600, SQUARE_LENGTH * 1.5)
    button_to_hold_sound_volume = Button(button_image, "", 50, WIDTH // 1.35, HEIGHT // 2.75 + 150, 600, SQUARE_LENGTH * 1.5)

    # Repositioned buttons to ensure that the volume sliding is not broken
    narrator_volume_scroller = Button(volume_button, "", 50, 697 + ((2 * narrator_volume) * (1200 - 697)), HEIGHT//2.75, SQUARE_LENGTH, SQUARE_LENGTH * 1.5) # 697 = most left, 1200 = most right
    sound_volume_scroller = Button(volume_button, "", 50, 697 + ((2 * sound_volume) * (1200 - 697)), HEIGHT//2.75 + 150, SQUARE_LENGTH, SQUARE_LENGTH * 1.5) 

    delete_save_button = Button(volume_button, "YES", 30, WIDTH//1.35, HEIGHT//2.75 + 300, SQUARE_LENGTH * 2.25, SQUARE_LENGTH * 2, BLACK)

    go_back_button =  Button(back_button, "", 30, WIDTH - 50, 50, SQUARE_LENGTH, SQUARE_LENGTH)

    settings_button_group = pygame.sprite.Group()
    settings_button_group.add(button_to_hold_narrator_volume, button_to_hold_sound_volume, 
                            narrator_volume_scroller, sound_volume_scroller,
                            delete_save_button, go_back_button)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.terminate()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if go_back_button.rect.collidepoint(event.pos): # If the back button is pressed by the mouse...
                        game.garbage_disposal([settings_title, narrator_volume_text, sound_volume_text,
                                              delete_save_text, narrator_volume_number, sound_volume_number,
                                              settings_button_group])
                        menu_backward.play()

                        # Updates the sounds
                        update_sounds(file="volume.txt", mode="write", volume1=narrator_volume, volume2=sound_volume)

                        # Make sure the user goes to a menu
                        try:
                            return_menu(True, True) # Back to the return menu
                        # If the menu does not satisfy the arguments, call the menu with none
                        except TypeError:
                            return_menu()
                    
                    # Take user to confirmation of deletion menu
                    if delete_save_button.rect.collidepoint(event.pos):
                        menu_forward.play()
                        confirm_data_deletion()

                    if narrator_volume_scroller.rect.collidepoint(event.pos):
                        narrator_moving = True
                    if sound_volume_scroller.rect.collidepoint(event.pos):
                        sound_moving = True

            if event.type == pygame.MOUSEMOTION: # If the mouse moves..
                # If the narrator scroll is being moved and is within the boundaries, move it
                if narrator_moving == True and LOWERBOUND <= narrator_volume_scroller.rect.x <= UPPERBOUND:
                    narrator_volume_scroller.rect.move_ip(event.rel[0], 0)
                    narrator_volume += (event.rel[0] / (2 * RANGE)) # Formula to change volume relative to movement

                    # Keeps the volume at minimum if minimum and maximum if maximum 
                    if narrator_volume >= 0.5:
                        narrator_volume = 0.5
                    if narrator_volume <= 0:
                        narrator_volume = 0

                    game.garbage_disposal([narrator_volume_number]) # Free the memory

                    # Update the text so the user knows the volume has changed
                    narrator_ui_volume = str(round(narrator_volume * 200)) 
                    narrator_volume_number = Text(narrator_ui_volume, WIDTH//2.25, HEIGHT//2.75, 30)

                    sounds.change_volume(narrator_sound_list, narrator_volume)

                if sound_moving == True and LOWERBOUND <= sound_volume_scroller.rect.x <= UPPERBOUND:

                    sound_volume_scroller.rect.move_ip(event.rel[0], 0)
                    sound_volume += (event.rel[0] / (2 * RANGE))

                    if sound_volume >= 0.5:
                        sound_volume = 0.5
                    if sound_volume <= 0:
                        sound_volume = 0

                    game.garbage_disposal([sound_volume_number])

                    sound_ui_volume = str(round(sound_volume * 200))
                    sound_volume_number = Text(sound_ui_volume, WIDTH//2.25, HEIGHT//2.75 + 150, 30)

                    sounds.change_volume(sound_list, sound_volume) # Change the volume of all sounds

            if event.type == pygame.MOUSEBUTTONUP: # If the mouse button is released..
                # If the scroll is released and is beyond the boundaries, bring it back to the boundaries
                if narrator_moving == True:
                    if narrator_volume_scroller.rect.x < LOWERBOUND:
                        narrator_volume_scroller.rect.x = LOWERBOUND
                    if narrator_volume_scroller.rect.x > UPPERBOUND:
                        narrator_volume_scroller.rect.x = UPPERBOUND

                if sound_moving == True:
                    if sound_volume_scroller.rect.x < LOWERBOUND:
                        sound_volume_scroller.rect.x =  LOWERBOUND
                    if sound_volume_scroller.rect.x > UPPERBOUND:
                        sound_volume_scroller.rect.x = UPPERBOUND

                narrator_moving = False
                sound_moving = False

        
        game.generate_background(background2)

        settings_title.update()
        narrator_volume_text.update()
        sound_volume_text.update()
        delete_save_text.update()
        narrator_volume_number.update()
        sound_volume_number.update()

        settings_button_group.update()

        game.update_state()

def confirm_data_deletion():
    """Menu for confirming that the data should be deleted."""

    # Creating a see-through background
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((20, 20, 20))
    overlay_rect = overlay.get_rect(topleft = (0, 0))

    # EVENT LOOP
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.terminate()
            # If the user presses the left mouse button, check if they press a button
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # If the user presses 'no', go back to the settings menu
                    if no_button.rect.collidepoint(event.pos):
                        menu_backward.play()
                        settings_menu()
                    # If the user presses 'yes', reset all the data in the game and the file and go back to the settings menu
                    if yes_button.rect.collidepoint(event.pos):
                        reset_levels(list_of_levels)
                        game.update_file("gamedata.txt", get_unlocked_level_number(list_of_levels))
                        menu_forward.play()
                        settings_menu()

        # Update the background
        overlay.set_alpha(2) # 7 -> 2
        screen.blit(overlay, overlay_rect)

        # Update GUI
        warning_text.update()
        data_deletion_group.update()

        pygame.display.update() # Use this and don't update FPS - Updating FPS creates fade out effect

def level_selection():
    """Generates the level selection menu where the user can select a level to play."""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if go_back_button_2.rect.collidepoint(event.pos):
                        game.garbage_disposal([level_selection_title, level_selection_button_group])
                        menu_backward.play()
                        main_menu()
                    # For each level that exists in the menu, check if the player has pressed it
                    for level in level_selection_button_group:
                        if isinstance(level, Level):
                            level.go_to_level(event.pos)

            # TEST CODE - DELETE WHEN USED
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u:
                    get_unlocked_level_number(list_of_levels)
                if event.key == pygame.K_l:
                    reset_levels(list_of_levels)

        game.generate_background(background4)

        level_selection_title.update()

        level_selection_button_group.update()

        game.update_state()

def win_menu(level):
    """Generates the win menu.""" 
    transparent = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA) # Background with editable transparency
    transparent.fill((100, 100, 0)) # Yellow background - BLACK DID NOT WORK :(
    transparent_rect = transparent.get_rect(topleft=(0, 0))

    player_move_sound.stop() # Fixes bug with win sound not playing sometimes
    win_sound.play() # Plays a random winning narrator sound

    # 20% to play a random winning narration sound
    if random.randint(0, 4) == 3:
        win_menu_sound = pygame.mixer.Sound(random.choice(sounds.win_state_sounds))
        win_menu_sound.set_volume(narrator_volume)
        win_menu_sound.play() # Plays a random winning narration sound
    
    level_to = str(level.__name__).split("_") # Gets the name of the level into a list
    level_to[1] = str(int(level_to[1]) + 1) # Adds one to the number in the level name
    next_level_name = "_".join(level_to) # Puts the level name back all together
    next_level = globals().get(next_level_name) # Turns the string into a function

    level_button =  f'{next_level_name}_button' # The next level's name relative to the naming scheme

    try:
        globals().get(level_button).locked = False # Unlocks the level
    # Don't unlock the level if the level doesn't exist
    except AttributeError:
        pass

    game.update_file("gamedata.txt", get_unlocked_level_number(list_of_levels)) # Write how many levels are unlocked

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Transport player to next level if they want to.
                    if next_level_button.rect.collidepoint(event.pos):
                        menu_forward.play()

                        # Try to stop the sound if it is defined
                        try:
                            win_menu_sound.stop() # Stops any sounds from overlapping
                        except UnboundLocalError:
                            pass
                        
                        # Go to the level selection if a new level isn't available
                        try:
                            next_level()
                        except TypeError:
                            level_selection()

                    # Go back to level selection if you press the right button
                    if go_back_to_levels_button.rect.collidepoint(event.pos):
                        menu_backward.play()
                        level_selection()

        transparent.set_alpha(1)
        screen.blit(transparent, transparent_rect)

        win_buttons.update()
        win_shadow.update()
        win_title.update()

        pygame.display.update() # So that there is no animation - DO NOT USE game.update_state()

def pause_menu(level):
    """Want to pause the game? This procedure does that."""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA) # Overlays the level translucent
    overlay.fill((10, 10, 10)) # Grey
    overlay_rect = overlay.get_rect(topleft = (0, 0))

    # Event loop:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if to_level_select_button.rect.collidepoint(event.pos):
                        menu_backward.play()
                        level_selection()
                    if settings_button.rect.collidepoint(event.pos):
                        menu_forward.play()
                        settings_menu(level)
                    if resume_button.rect.collidepoint(event.pos):
                        menu_backward.play()
                        level(True, False) # Load the level back in but do not instantly pause it

        # Add the background#
        overlay.set_alpha(7) # Sets the alpha value - How translucent is it????
        screen.blit(overlay, overlay_rect)

        # Update the screen with GUI elements
        pause_title.update()
        pause_group.update()

        # DO NOT USE game.upadte_state() - A still background is required
        pygame.display.update()
        #game.update_state()

# ----------------------------------------------------------------------- #

# This is the main file
if __name__ == "__main__":
    main_menu()