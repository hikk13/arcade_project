import arcade


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.BLUE)

    def on_draw(self):
        self.clear()
