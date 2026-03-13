import arcade

from menu import MenuView

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 1024
SCREEN_TITLE = "Siege of the Castle"


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, center_window=True)
        self.background_music = arcade.load_sound(":resources:/music/1918.mp3")
        self.background_music.play(loop=True, volume=0.5)

def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    menu_view = MenuView()
    game.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()
