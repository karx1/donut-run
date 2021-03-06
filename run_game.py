#!/usr/bin/env python

import arcade
import math
import random
from views import GameOverView, OpeningView
from globals import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_TITLE,
    SPRITE_SCALING,
    MOVEMENT_SPEED,
)
from text import draw_text
from sprites import Enemy, Player

class Game(arcade.View):
    def __init__(self):
        super().__init__()

        self.player_list = None
        self.player_sprite = None

        self.bullet_list = None
        self.enemy_bullet_list = None

        self.wall_list = None
        self.donut_list = None
        self.enemy_list = None

        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False

        self.physics_engine = None
        self.enemy_engines = None

        self.level = 0
        self.score = 0

        arcade.set_background_color(arcade.color.DARK_BROWN)

    def on_draw(self):
        arcade.start_render()

        self.player_list.draw()
        self.bullet_list.draw()
        self.wall_list.draw()
        self.donut_list.draw()
        self.enemy_list.draw()
        self.enemy_bullet_list.draw()

        # Draw score and level text
        draw_text(f"Wave: {self.level + 1}", 10, 40, arcade.color.WHITE, 14)
        draw_text(f"Score: {self.score}", 10, 20, arcade.color.WHITE, 14)

    def on_update(self, delta_time: float):
        for engine in self.enemy_engines:
            engine.update()

        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0

        if self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = MOVEMENT_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.change_y = -MOVEMENT_SPEED
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = MOVEMENT_SPEED

        # self.player_list.update()

        if self.player_sprite.last_mouse_x and self.player_sprite.last_mouse_y:
            start_x = self.player_sprite.center_x
            start_y = self.player_sprite.center_y

            x_diff = self.player_sprite.last_mouse_x - start_x
            y_diff = self.player_sprite.last_mouse_y - start_y
            angle = math.atan2(y_diff, x_diff)

            self.player_sprite.angle = math.degrees(angle)

        donut_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.donut_list)

        if len(donut_hit_list) > 0:
            for donut in donut_hit_list:
                donut.remove_from_sprite_lists()
                self.score += 1

        for bullet in self.bullet_list:
            wall_hit_list = arcade.check_for_collision_with_list(bullet, self.wall_list)
            enemy_hit_list = arcade.check_for_collision_with_list(
                bullet, self.enemy_list
            )

            if len(wall_hit_list) > 0:
                bullet.remove_from_sprite_lists()

            if len(enemy_hit_list) > 0:
                bullet.remove_from_sprite_lists()
                for enemy in enemy_hit_list:
                    enemy.remove_from_sprite_lists()

            # If bullet flies offscreen, remove it
            if (
                bullet.bottom > SCREEN_WIDTH
                or bullet.top < 0
                or bullet.right < 0
                or bullet.left > SCREEN_WIDTH
            ):
                bullet.remove_from_sprite_lists()

        for bullet in self.enemy_bullet_list:
            wall_hit_list = arcade.check_for_collision_with_list(bullet, self.wall_list)
            donut_hit_list = arcade.check_for_collision_with_list(bullet, self.donut_list)
            player_hit = arcade.check_for_collision(bullet, self.player_sprite)

            if player_hit:
                self.player_sprite.remove_from_sprite_lists()
                view = GameOverView(self.window, Game, self.level + 1, self.score)
                self.window.show_view(view)

            if len(wall_hit_list) > 0:
                bullet.remove_from_sprite_lists()
            
            if len(donut_hit_list) > 0:
                bullet.remove_from_sprite_lists()
                for donut in donut_hit_list:
                    donut.remove_from_sprite_lists()

            if (
                bullet.bottom > SCREEN_WIDTH
                or bullet.top < 0
                or bullet.right < 0
                or bullet.left > SCREEN_WIDTH
            ):
                bullet.remove_from_sprite_lists()

        self.bullet_list.update()
        # self.wall_list.update()
        for enemy in self.enemy_list:
            if not arcade.has_line_of_sight(
                self.player_sprite.position, enemy.position, self.wall_list
            ):
                enemy.follow_sprite(self.player_sprite)
            else:
                enemy.stop()

                x_diff = self.player_sprite.center_x - enemy.center_x
                y_diff = self.player_sprite.center_y - enemy.center_y

                angle = math.atan2(y_diff, x_diff)

                enemy.angle = math.degrees(angle)

                odds = 200
                adj_odds = int(odds * (1 / 60) / delta_time)
                if random.randrange(adj_odds) == 0:
                    bullet = arcade.Sprite("assets/bullet.png", 0.08)
                    bullet.center_x = enemy.center_x
                    bullet.center_y = enemy.center_y
                    bullet.angle = math.degrees(angle)

                    bullet.change_x = math.cos(angle) * MOVEMENT_SPEED
                    bullet.change_y = math.sin(angle) * MOVEMENT_SPEED
                    self.enemy_bullet_list.append(bullet)

        self.enemy_list.update()

        self.physics_engine.update()

        self.enemy_bullet_list.update()

        if len(self.enemy_list) == 0:
            self.level += 1
            self.setup(self.level, self.score)

        return super().on_update(delta_time)

    def setup(self, level, score):

        self.level = level
        self.score = score

        self.player_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.donut_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()

        self.player_sprite = Player("assets/player.png", SPRITE_SCALING * 2)
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 50
        self.player_list.append(self.player_sprite)

        for _ in range((self.level + 1) * 2):
            donut = arcade.Sprite("assets/donut.png", 1)


            donut_placed = False

            while not donut_placed:
                donut.center_x = random.randrange(SCREEN_WIDTH)
                donut.center_y = random.randrange(SCREEN_HEIGHT)

                donut_hit_list = arcade.check_for_collision_with_list(
                    donut, self.donut_list
                )

                wall_hit_list = arcade.check_for_collision_with_list(
                    donut, self.wall_list
                )

                
                donut_placed = len(donut_hit_list) == 0 and len(wall_hit_list) == 0
            
            self.donut_list.append(donut)

        for _ in range(25):
            wall = arcade.Sprite("assets/wall.png", 1)

            wall_placed = False

            # Keep trying until success
            while not wall_placed:
                wall.center_x = random.randrange(SCREEN_WIDTH)
                wall.center_y = random.randrange(SCREEN_HEIGHT)

                wall_hit_list = arcade.check_for_collision_with_list(
                    wall, self.wall_list
                )

                if len(wall_hit_list) == 0:
                    wall_placed = True

            self.wall_list.append(wall)

        self.enemy_engines = []
        for _ in range(self.level + 1):
            enemy = Enemy("assets/enemy.png", 1)

            enemy_placed = False

            # Keep trying until success
            while not enemy_placed:
                enemy.center_x = random.randrange(SCREEN_WIDTH)
                enemy.center_y = random.randrange(SCREEN_HEIGHT)

                enemy_hit_list = arcade.check_for_collision_with_list(
                    enemy, self.enemy_list
                )

                if len(enemy_hit_list) == 0:
                    enemy_placed = True

            engine = arcade.PhysicsEngineSimple(enemy, self.wall_list)
            self.enemy_engines.append(engine)

            self.enemy_list.append(enemy)

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite, self.wall_list
        )

    def on_key_press(self, key, modifiers):
        # If the player presses a key, update the speed
        if key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        elif key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.D:
            self.right_pressed = True

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False
        elif key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False
        elif key == arcade.key.W:
            self.up_pressed = False
        elif key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.D:
            self.right_pressed = False

    def on_mouse_motion(self, x, y, dx, dy):
        """ Handle Mouse Motion """

        start_x = self.player_sprite.center_x
        start_y = self.player_sprite.center_y

        x_diff = x - start_x
        y_diff = y - start_y
        angle = math.atan2(y_diff, x_diff)

        self.player_sprite.angle = math.degrees(angle)
        self.player_sprite.last_mouse_x = x
        self.player_sprite.last_mouse_y = y

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        bullet = arcade.Sprite("assets/bullet.png", 0.08)

        bullet.center_x = self.player_sprite.center_x
        bullet.center_y = self.player_sprite.center_y

        x_diff = x - self.player_sprite.center_x
        y_diff = y - self.player_sprite.center_y
        angle = math.atan2(y_diff, x_diff)

        bullet.angle = math.degrees(angle)
        self.player_sprite.angle = math.degrees(angle)
        self.player_sprite.last_mouse_x = x
        self.player_sprite.last_mouse_y = y

        bullet.change_x = math.cos(angle) * MOVEMENT_SPEED
        bullet.change_y = math.sin(angle) * MOVEMENT_SPEED

        self.bullet_list.append(bullet)


def main():
    """ Main method """
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    view = OpeningView(window, Game)
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()
