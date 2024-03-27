import pygame
import main
import random
import sounds
from os.path import join

class Enemy:
    """The home of all enemies in the Logical Psycho game."""

    class Static(pygame.sprite.Sprite):
        def __init__(self, x: int, y: int):
            """Enemy that does nothing. It sits still and menacingly."""
            super().__init__()
            self.image_path = join("Assets", "Enemy", "StaticBeing", "Staticbeing.png")
            self.frames = [main.get_sprite_sheet(self.image_path, (0, 0, 16, 16)),
                           main.get_sprite_sheet(self.image_path, (16, 0, 16, 16))]
            self.index: float = 0
            self.image_normal = self.frames[self.index].convert_alpha()
            self.image = pygame.transform.scale(self.image_normal, (main.SQUARE_LENGTH, main.SQUARE_LENGTH))
            self.rect = self.image.get_rect(topleft = (x, y))
        
        def check_collision(self, moving_thing):
            """Checks if a moving thing is colliding with the static enemy."""

            if moving_thing.rect == self.rect:
                return True
            
            return False
        
        def set_image(self, index: int):
            """Sets the image of the object"""
            self.image_normal = self.frames[int(index)].convert_alpha()
            self.image = pygame.transform.scale(self.image_normal, (main.SQUARE_LENGTH, main.SQUARE_LENGTH))

        def update(self):
            """Updates the object."""

            # Update the image every N seconds such that denominator = n * 1000
            self.index += (60 / 1100)

            # If the index is out of bounds, reset it
            if not 0 <= self.index < len(self.frames):
                self.index = 0

            # Set the image of the sprite
            self.set_image(self.index)

    class Dynamic(pygame.sprite.Sprite):

        def __init__(self, x: int, y: int, frequency: int = 3, delay: int = 0, style: str = "seek"):
            """
            Enemy that pinpoints the player location and moves accordingly.

            Frequency is how many times the enemy moves per second. This value should not exceed 6 otherwise things get messy.
            
            Delay is how many frames the enemy should wait before moving. If you want the enemy to wait for 1/2 a second,
            you can put 30 in as the argument.

            There are 4 different styles to choose from. These indicate how the enemy moves:

            1 - Randomised: Chooses a random space to move to
            2 - Seek (default): Moves optimally towards player
            3 - Burst: Move 3 times in a row and then wait for a little bit
            4 - Axisbound: Moves only on the X or Y axis
            """
            super().__init__()
            self.image_path = join("Assets", "Enemy", "DynamicBeing", "DynamicBeing.png")
            self.frames = [main.get_sprite_sheet(self.image_path, (0, 0, 16, 16)),
                           main.get_sprite_sheet(self.image_path, (16, 0, 16, 16))]
            self.index: float = 0
            self.image_normal = self.frames[self.index].convert_alpha()
            self.image = pygame.transform.scale(self.image_normal, (main.SQUARE_LENGTH, main.SQUARE_LENGTH))
            self.rect = self.image.get_rect(topleft = (x, y))

            # Sound attributes
            self.sound = pygame.mixer.Sound(sounds.effect_sounds[6])
            self.volume = main.sound_volume
            self.sound.set_volume(self.volume)

            # Movement attributes
            self.dy = 0
            self.dx = 0
            self.current_frame = 0
            self.target_frame = 10
            self.moving = False
            self.player_position = []
            self.style = style

            # Burst algorithm attributes
            self.burst_complete = False
            self.burst_count = 0
            self.burst_direction = None

            # Moving attributes for movement bug
            self.last_move = ""
            self.last_enemy_position = []
            self.translated_distances = []
            self.movement_choices = []
            self.bash_wall = False # Ensures that the algorithm detects wall bashing

            # Axisbound algorithm attributes
            if self.style.lower() ==  "axisbound":
                self.movement_choices = random.choice([["L", "R"], ["U", "D"]])

            # Creating timer for movement
            self.since_movement = 0 - delay
            self.target_movement_time = round(main.FPS / frequency)

        def seek(self):
            """Optimised movement towards enemy."""
            # Other distances assuming that the enemy moved in that direction

            distance_if_left = round(((self.player_position[1] - self.rect.y) ** 2 + (self.player_position[0] - (self.rect.x - 80)) ** 2) ** 0.5, 3)
            distance_if_right = round(((self.player_position[1] - self.rect.y) ** 2 + (self.player_position[0] - (self.rect.x + 80)) ** 2) ** 0.5, 3)
            distance_if_up = round(((self.player_position[1] - (self.rect.y - 80)) ** 2 + (self.player_position[0] - self.rect.x) ** 2) ** 0.5, 3)
            distance_if_down = round(((self.player_position[1] - (self.rect.y + 80)) ** 2 + (self.player_position[0] - self.rect.x) ** 2) ** 0.5, 3)

            # Action to take if the enemy does not change position / hits a wall
            if [self.rect.x, self.rect.y] == self.last_enemy_position:
                # Gets the move that leads to such a condition and removes it
                self.translated_distances.remove(self.translated_distances[self.movement_choices.index(self.last_move)])
                # Removes the respective direction
                self.movement_choices.remove(self.last_move)
                self.bash_wall = True

            else:
                # List of all distances
                self.translated_distances = [distance_if_left, distance_if_right, distance_if_up, distance_if_down]
                self.movement_choices = ["L", "R", "U", "D"]

                # If there is a last move..
                if self.last_move != "" and self.bash_wall:
                    # Find the opposing direction to the last movement
                    opposing_direction = self.reverse_movement(self.last_move)
                    # Remove that direction from being accessible
                    self.translated_distances.remove(self.translated_distances[self.movement_choices.index(opposing_direction)])
                    self.movement_choices.remove(opposing_direction)
                    self.bash_wall = False

            # Finds the best distance between the player and the enemy
            best_distance = min(self.translated_distances)

            # Index to find the respective direction
            index = self.translated_distances.index(best_distance)
            choice_of_movement = self.movement_choices[index] # Direction

            # Stores the direction of the enemy's movement and the coordinates of the payer
            self.last_move = choice_of_movement
            self.last_enemy_position = [self.rect.x, self.rect.y]

            # Move in the direction that corresponds to the letter
            if choice_of_movement == "U":
                self.dy = -(main.SQUARE_LENGTH / self.target_frame)
                self.dx = 0

            if choice_of_movement == "D":
                self.dy = (main.SQUARE_LENGTH / self.target_frame)
                self.dx = 0

            if choice_of_movement == "L":
                self.dy = 0
                self.dx = -(main.SQUARE_LENGTH / self.target_frame)

            if choice_of_movement == "R":
                self.dy = 0
                self.dx = (main.SQUARE_LENGTH / self.target_frame)

            # Reset the movement frames so that the enemy moves
            self.moving = True
            self.get_volume()
            self.sound.play()

        def randomised(self):
            """Enemy moves randomly."""

            # List of all directions to move
            self.movement_choices = ["L", "R", "U", "D"]
            choice_of_movement = random.choice(self.movement_choices) # Direction

            # Move in the direction that corresponds to the letter
            if choice_of_movement == "U":
                self.dy = -(main.SQUARE_LENGTH / self.target_frame)
                self.dx = 0

            if choice_of_movement == "D":
                self.dy = (main.SQUARE_LENGTH / self.target_frame)
                self.dx = 0

            if choice_of_movement == "L":
                self.dy = 0
                self.dx = -(main.SQUARE_LENGTH / self.target_frame)

            if choice_of_movement == "R":
                self.dy = 0
                self.dx = (main.SQUARE_LENGTH / self.target_frame)

            # Reset the movement frames so that the enemy moves
            self.moving = True
            self.get_volume()
            self.sound.play()

        def burst(self):
            """Allows the enemy to move thrice before stopping temporarily."""
            # List of all directions to move
            self.movement_choices = ["L", "R", "U", "D"]
            choice_of_movement = random.choice(self.movement_choices) # Direction
            
            # Save the current direction
            if self.burst_direction is None:
                self.burst_direction = choice_of_movement

            # Override the current direction with the burst direction
            else:
                choice_of_movement = self.burst_direction

            # Move in the direction that corresponds to the letter
            if choice_of_movement == "U":
                self.dy = -(main.SQUARE_LENGTH / self.target_frame)
                self.dx = 0

            if choice_of_movement == "D":
                self.dy = (main.SQUARE_LENGTH / self.target_frame)
                self.dx = 0

            if choice_of_movement == "L":
                self.dy = 0
                self.dx = -(main.SQUARE_LENGTH / self.target_frame)

            if choice_of_movement == "R":
                self.dy = 0
                self.dx = (main.SQUARE_LENGTH / self.target_frame)

            # Reset the movement frames so that the enemy moves
            self.moving = True
            self.get_volume()
            self.sound.play()

            # Increment the counter
            if self.burst_direction:
                self.burst_count += 1

                # Burst movement can only happen 3 times in a row
                if self.burst_count == 3:
                    self.burst_complete = True
                      
        def axisbound(self):
            """A very normal algorithm."""
            choice_of_movement = random.choice(self.movement_choices) # Direction

            # Move in the direction that corresponds to the letter
            if choice_of_movement == "U":
                self.dy = -(main.SQUARE_LENGTH / self.target_frame)
                self.dx = 0

            if choice_of_movement == "D":
                self.dy = (main.SQUARE_LENGTH / self.target_frame)
                self.dx = 0

            if choice_of_movement == "L":
                self.dy = 0
                self.dx = -(main.SQUARE_LENGTH / self.target_frame)

            if choice_of_movement == "R":
                self.dy = 0
                self.dx = (main.SQUARE_LENGTH / self.target_frame)

            # Reset the movement frames so that the enemy moves
            self.moving = True
            self.get_volume()
            self.sound.play()

        def movement(self):
            """Moves the enemy closer to the player using a chosen algorithm.""" 
            
            style = self.style.lower()

            if style == "randomised":
                self.randomised()

            if style == "burst":
                self.burst()

            if style == "axisbound":
                self.axisbound()

            if style == "seek":
                self.seek()

        def reverse_movement(self, movement_choice):
            """Reverses a movement choice. Assume that the movement choice is one of 4 characters below."""

            # Reverser dictionary
            reverser = {
                "L": "R",
                "R": "L",
                "U": "D",
                "D": "U"
            }

            return reverser[movement_choice]
            
        def check_collision(self, moving_thing):
            """Checks if a moving thing is colliding with the static enemy."""

            # Check if the two rectangles are colliding
            if self.rect.colliderect(moving_thing.rect): 
                return True
                
            return False
        
        def get_volume(self):
            """Gets the volume of the sound."""

            # Open the file in read mode
            with open("volume.txt", "r") as file:
                file_copy = file.readlines()

                # Obtains the volume from the file
                self.volume = float(file_copy[1].replace("\n", ""))
                self.sound.set_volume(self.volume)

        def get_player_position(self, player_position):
            """Gets the player's position as a rectangle and extracts the x and y coordinates."""
            self.player_position = [player_position.x, player_position.y]
         
        def set_image(self, index: int):
            """Sets the image of the object"""
            self.image_normal = self.frames[int(index)].convert_alpha()
            self.image = pygame.transform.scale(self.image_normal, (main.SQUARE_LENGTH, main.SQUARE_LENGTH))

        def update(self):
            """Updates the object."""
            self.index += (60 / 1100)

            if not 0 <= self.index < len(self.frames):
                self.index = 0

            self.set_image(self.index)

            # Only execute the code if the player can move
            if self.moving:
                # Move the enemy if the enemy has not moved to where it must
                if self.current_frame < self.target_frame:
                    self.rect.y += self.dy
                    self.rect.x += self.dx 
                    self.current_frame += 1

                # Don't let the enemy move more than it needs to
                if self.current_frame >= self.target_frame:
                    
                    # Ensuring the burst is created
                    if self.burst_direction is not None and not self.burst_complete:
                        self.moving = False
                        self.current_frame = 0
                        self.since_movement = self.target_movement_time - 2

                    # Add the 1 second delay and reset statistics to loop bursting
                    elif self.burst_complete:
                        self.moving = False
                        self.current_frame = 0
                        self.since_movement = -60
                        self.burst_complete = False
                        self.burst_count = 0
                        self.burst_direction = None

                    # Normal option
                    else:
                        self.moving = False
                        self.current_frame = 0
                        self.since_movement = 0

            # Count the frames the enemy has not moved
            else:
                self.since_movement += 1

                # If a certain amount of time has elapsed, allow the enemy to move
                if self.since_movement >= self.target_movement_time and not self.moving:
                    self.movement()

def enemy_factory(enemies: list, type):
        """Creates enemies based upon a list of enemies."""

        # Have a list to store all the enemies we want to add to the group
        enemy_list = []

        # For each enemy, map their coordinates properly and add them to a list
        for enemy in enemies:
            x = enemy[0] * main.SQUARE_LENGTH
            y = enemy[1] * main.SQUARE_LENGTH
            enemy_list.append(type(x, y))

        return enemy_list