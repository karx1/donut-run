import arcade
from globals import SCREEN_WIDTH, SCREEN_HEIGHT

class GameOverView(arcade.View):
    def __init__(self, window: arcade.Window, game: arcade.View):
        self.game = game

        super().__init__(window=window)

        arcade.set_background_color(arcade.color.AERO_BLUE)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("GAME OVER", SCREEN_WIDTH/2, SCREEN_HEIGHT/2,
                         arcade.color.BLACK, font_size=50, anchor_x="center")
        arcade.draw_text("Click to restart", SCREEN_WIDTH/2, SCREEN_HEIGHT/2-75,
                         arcade.color.GRAY, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = self.game()
        game_view.setup()
        self.window.show_view(game_view)
