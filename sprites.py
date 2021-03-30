import arcade
import math
from globals import SCREEN_WIDTH, SCREEN_HEIGHT
import random

class Player(arcade.Sprite):
    """ Player Class """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.last_mouse_x, self.last_mouse_y = None, None

    def update(self):
        """ Move the player """
        # Move player.
        # Remove these lines if physics engine is moving player.
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Check for out-of-bounds
        if self.left < 0:
            self.left = 0
        elif self.right > SCREEN_WIDTH - 1:
            self.right = SCREEN_WIDTH - 1

        if self.bottom < 0:
            self.bottom = 0
        elif self.top > SCREEN_HEIGHT - 1:
            self.top = SCREEN_HEIGHT - 1


class Enemy(arcade.Sprite):
    def follow_sprite(self, sprite):
        if random.randrange(100) == 0:
            start_x = self.center_x
            start_y = self.center_y

            # Get the destination location for the enemy
            dest_x = sprite.center_x
            dest_y = sprite.center_y

            # Do math to calculate how to get the bullet to the destination.
            # Calculation the angle in radians between the start points
            # and end points. This is the angle the bullet will travel.
            x_diff = dest_x - start_x
            y_diff = dest_y - start_y
            angle = math.atan2(y_diff, x_diff)

            self.angle = math.degrees(angle)

            # Taking into account the angle, calculate our change_x
            # and change_y. Velocity is how fast the enemy travels.
            self.change_x = math.cos(angle) * 2
            self.change_y = math.sin(angle) * 2