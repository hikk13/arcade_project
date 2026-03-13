import arcade

from arcade.gui import UIManager, UITextureButton, UILabel
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout

from game_window import GameView


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.fon = arcade.load_texture("images/fon.png")
        self.title_board = arcade.load_texture("images/menu_board.png")

        self.manager = UIManager()
        self.manager.enable()

        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=20)

        self.setup_widgets()

        self.anchor_layout.add(self.box_layout)
        self.manager.add(self.anchor_layout)

    def setup_widgets(self):
        title = UILabel(
            text="Siege of the Castle",
            font_name="Showcard Gothic",
            font_size=40,
            text_color=arcade.color.WHITE,
            width=300,
            align="center"
        )
        self.box_layout.add(title)

        texture_normal = arcade.load_texture(":resources:/gui_basic_assets/button/red_normal.png")
        texture_hovered = arcade.load_texture(":resources:/gui_basic_assets/button/red_hover.png")
        texture_pressed = arcade.load_texture(":resources:/gui_basic_assets/button/red_press.png")

        play_button = UITextureButton(
            texture=texture_normal,
            texture_hovered=texture_hovered,
            texture_pressed=texture_pressed,
            text="Играть",
            scale=1.5
        )
        play_button.on_click = self.on_click_play
        self.box_layout.add(play_button)

        exit_button = UITextureButton(
            texture=texture_normal,
            texture_hovered=texture_hovered,
            texture_pressed=texture_pressed,
            text="Выйти",
            scale=1.5
        )
        exit_button.on_click = lambda event: self.window.close()
        self.box_layout.add(exit_button)

    def on_click_play(self, event):
        game_view = GameView()
        game_view.setup()
        self.window.show_view(game_view)

    def on_draw(self):
        self.clear()

        arcade.draw_texture_rect(
            self.fon, arcade.rect.XYWH(self.width // 2, self.height // 2, self.width, self.height)
        )

        arcade.draw_texture_rect(
            self.title_board, arcade.rect.XYWH(self.width // 2, 600, 600, 70)
        )

        self.manager.draw()

    def on_show_view(self):
        self.window.set_size(self.window.width, self.window.height)

    def on_hide_view(self):
        self.manager.disable()
