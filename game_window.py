import arcade
from random import choice, uniform

from arcade import Camera2D
from arcade.gui import UIManager, UILabel, UIDropdown, UITextureButton
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
from arcade.particles import FadeParticle, Emitter, EmitBurst

from towers import Tower, Bullet, Barrier, Barricade
from enemies import Militiaman, Lancer, Knight, Ram
from wave_system import WaveManager

from pyglet.graphics import Batch

# Система частиц
SPARK_TEX = [
    arcade.make_soft_circle_texture(8, arcade.color.PASTEL_YELLOW),
    arcade.make_soft_circle_texture(8, arcade.color.PEACH),
    arcade.make_soft_circle_texture(8, arcade.color.BABY_BLUE),
    arcade.make_soft_circle_texture(8, arcade.color.ELECTRIC_CRIMSON),
]

def gravity_drag(p):
    p.change_y += -0.03
    p.change_x *= 0.92
    p.change_y *= 0.92


def make_explosion(x, y, count=80):
    return Emitter(
        center_xy=(x, y),
        emit_controller=EmitBurst(count),
        particle_factory=lambda e: FadeParticle(
            filename_or_texture=choice(SPARK_TEX),
            change_xy=arcade.math.rand_in_circle((0.0, 0.0), 9.0),
            lifetime=uniform(0.5, 1.1),
            start_alpha=255, end_alpha=0,
            scale=uniform(0.35, 0.6),
            mutation_callback=gravity_drag,
        ),
    )


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.emitters = []

        # Графический менеджер
        self.camera = None
        self.ui_manager = UIManager()
        self.ui_manager.enable()
        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=10)
        self.anchor_layout.add(self.box_layout)
        self.ui_manager.add(self.anchor_layout)
        self.is_zoom = False

        # Позиции и цены башен с баррикадой
        self.tower_positions = {
            "Северо-западная позиция": (18.5 * 32, 15.5 * 32), "Северо-восточная позиция": (26.5 * 32, 15.5 * 32),
            "Юго-западная позиция": (18.5 * 32, 9.5 * 32), "Юго-восточная позиция": (26.5 * 32, 9.5 * 32),
            "Северная дорога": (22.5 * 32, 18.5 * 32), "Западная дорога": (14.5 * 32, 12.5 * 32),
            "Южная дорога":(22.5 * 32, 7.5 * 32), "Восточная дорога": (30.5 * 32, 12.5 * 32)
        }
        self.cost_towers = {"Баррикада": (10, 40), "Лучник": (20, 30), "Катапульта": (30, 60), "Баллиста": (25, 50)}

        # Атрибуты для размещения башен и баррикады
        self.current_building = None
        self.is_barricade = False

        # Позиции врагов
        self.enemies_position = {
            "Север": (720, 800), "Запад": (0, 400),
            "Юг": (720, 0), "Восток": (1440, 400)
        }

        # Текстуры кнопок
        self.texture_btn_normal = arcade.load_texture(":resources:/gui_basic_assets/button/red_normal.png")
        self.texture_btn_hovered = arcade.load_texture(":resources:/gui_basic_assets/button/red_hover.png")
        self.texture_btn_pressed = arcade.load_texture(":resources:/gui_basic_assets/button/red_press.png")

        self.gold = 150
        self.number_enemies = 0

        # Результаты
        self.time = 0
        self.count_defeated_enemies = 0
        self.spent_gold = 0

        self.batch = Batch()

    def setup(self):
        # Карта
        map_name = "map.tmx"
        tile_map = arcade.load_tilemap(map_name)
        self.ground = tile_map.sprite_lists["ground"]
        self.decorations = tile_map.sprite_lists["decorations"]

        # Замок и ворота
        self.castle = Barrier("images/towers/castle.png", center_x=720, center_y=410, hp=200)
        self.list_castle = arcade.SpriteList()
        self.list_castle.append(self.castle)

        self.list_gates = arcade.SpriteList()
        self.north_gate = Barrier("images/towers/gate.png", center_x=22.5 * 32, center_y=15.5 * 32, hp=150)
        self.west_gate = Barrier("images/towers/gate.png", center_x=18.5 * 32, center_y=12.5 * 32, hp=150)
        self.south_gate = Barrier("images/towers/gate.png", center_x=26.5 * 32, center_y=12.5 * 32, hp=150)
        self.east_gate = Barrier("images/towers/gate.png", center_x=22.5 * 32, center_y=9.5 * 32, hp=150)
        self.list_gates.extend([self.north_gate, self.west_gate, self.south_gate, self.east_gate])

        # Панель информации
        self.board = arcade.load_texture("images/board.png")

        self.amount_gold = arcade.Text(
            f"Золото: {self.gold}",
            1000,
            200,
            color=arcade.color.YELLOW,
            font_size=32,
            width=300,
            font_name="Showcard Gothic",
            batch=self.batch
        )

        self.amount_enemies = arcade.Text(
            f"Враги: {self.number_enemies}",
            1000,
            125,
            color=arcade.color.RED,
            font_size=32,
            width=300,
            font_name="Showcard Gothic",
            batch=self.batch
        )

        self.amount_hp = arcade.Text(
            f"Прочность замка: {self.castle.hp}",
            1000,
            50,
            color=arcade.color.WHITE,
            font_size=32,
            width=300,
            font_name="Showcard Gothic",
            batch=self.batch
        )

        # Система волн
        waves = [
            [{"type_enemy": "militiaman", "count": 5},
             {"type_enemy": "lancer", "count": 3}],

            [{"type_enemy": "militiaman", "count": 7},
             {"type_enemy": "lancer", "count": 5},
             {"type_enemy": "knight", "count": 3}],

            [{"type_enemy": "militiaman", "count": 10},
             {"type_enemy": "lancer", "count": 5},
             {"type_enemy": "lancer", "count": 5},
             {"type_enemy": "ram", "count": 2}]
        ]
        self.wave_manager = WaveManager(waves, self.spawn_enemy)

        # Списки спрайтов
        self.list_towers = arcade.SpriteList()
        self.list_barricades = arcade.SpriteList()
        self.list_enemies = arcade.SpriteList()
        self.list_bullets = arcade.SpriteList()

    def on_draw(self):
        self.clear()

        if self.camera:
            self.camera.use()

        self.ground.draw()
        self.decorations.draw()
        self.list_castle.draw()
        self.list_gates.draw()
        self.list_towers.draw()
        self.list_barricades.draw()
        self.list_enemies.draw()
        self.list_bullets.draw()

        arcade.draw_texture_rect(
            self.board, arcade.rect.XYWH(1184, 130, 512, 256), alpha=225
        )

        self.batch.draw()

        for e in self.emitters:
            e.draw()

        if self.is_zoom:
            arcade.draw_texture_rect(
                self.board, arcade.rect.XYWH(720, 400, 500, 100), alpha=225
            )
            self.ui_manager.draw()

    def on_update(self, delta_time):
        if self.wave_manager.wave_active:
            self.wave_manager.update(delta_time)
            self.time += delta_time

        # Стрельба башен
        for tower in self.list_towers:
            tower.shot_timer += delta_time
            if tower.shot_timer >= tower.interval:
                attacked_enemy = None
                min_distance = tower.firing_range
                for enemy in self.list_enemies:
                    distance = arcade.get_distance_between_sprites(tower, enemy)
                    if distance <= tower.firing_range and distance < min_distance:
                        attacked_enemy = enemy
                        min_distance = distance
                if attacked_enemy:
                    if tower.type_tower == "Archer":
                        texture = arcade.load_texture("images/towers/arrow.png")
                    elif tower.type_tower == "Catapult":
                        texture = arcade.load_texture("images/towers/boulder.png")
                    else:
                        texture = arcade.load_texture("images/towers/bolt.png")

                    bullet = Bullet(texture, tower, attacked_enemy)
                    self.list_bullets.append(bullet)
                    tower.shot_timer = 0

        # Проверка попадания снаряда во врага
        for bullet in self.list_bullets:
            enemies_hit_list = arcade.check_for_collision_with_list(bullet, self.list_enemies)

            if enemies_hit_list:
                for enemy in enemies_hit_list:
                    enemy.hp -= bullet.damage
                    bullet.remove_from_sprite_lists()
                    if enemy.hp <= 0:
                        self.emitters.append(make_explosion(enemy.center_x, enemy.center_y))
                        self.number_enemies -= 1
                        self.count_defeated_enemies += 1
                        self.gold += 20
                        self.amount_enemies.text = f"Враги: {self.number_enemies}"
                        self.amount_gold.text = f"Золото: {self.gold}"
                        enemy.remove_from_sprite_lists()

            if arcade.get_distance_between_sprites(bullet.tower, bullet) >= bullet.firing_range:
                bullet.remove_from_sprite_lists()

        # Проверка столкновений врагов с баррикадой, воротами или замком
        for enemy in self.list_enemies:
            barricade_hit_list = arcade.check_for_collision_with_list(enemy, self.list_barricades)
            gates_hit_list = arcade.check_for_collision_with_list(enemy, self.list_gates)
            castle_attack = arcade.check_for_collision_with_list(enemy, self.list_castle)

            if barricade_hit_list:
                enemy.is_attacking = True
                enemy.is_walking = False
                for barricade in barricade_hit_list:
                    barricade.hp -= enemy.damage * delta_time
                    if barricade.hp <= 0:
                        barricade.remove_from_sprite_lists()
            elif gates_hit_list:
                enemy.is_attacking = True
                enemy.is_walking = False
                for gate in gates_hit_list:
                    gate.hp -= enemy.damage * delta_time
                    if gate.hp <= 0:
                        gate.remove_from_sprite_lists()
            elif castle_attack:
                enemy.is_attacking = True
                enemy.is_walking = False
                for castle in castle_attack:
                    castle.hp -= enemy.damage * delta_time
                    self.amount_hp.text = f"Прочность замка: {self.castle.hp}"
                    if castle.hp <= 0:
                        castle.remove_from_sprite_lists()
                        game_over_view = GameOverView()
                        self.window.show_view(game_over_view)
            else:
                enemy.is_attacking = False
                enemy.is_walking = True

        self.list_enemies.update(delta_time)
        self.list_enemies.update_animation(delta_time)
        self.list_bullets.update(delta_time)

        emitters_copy = self.emitters.copy()
        for e in emitters_copy:
            e.update(delta_time)
        for e in emitters_copy:
            if e.can_reap():
                self.emitters.remove(e)

        if self.wave_manager.count_waves == len(self.wave_manager.waves) and self.number_enemies == 0:
            game_win_view = GameWinView(self, self.time, self.count_defeated_enemies, self.spent_gold)
            self.window.show_view(game_win_view)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE and not self.is_zoom:
            self.wave_manager.start_wave()
            self.number_enemies = len(self.wave_manager.queue_enemies)
            self.amount_enemies.text = f"Враги: {self.number_enemies}"
        elif key == arcade.key.ESCAPE:
            pause_view = PauseView(self)
            self.window.show_view(pause_view)

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.wave_manager.wave_active:
            if button == arcade.MOUSE_BUTTON_LEFT and not self.is_zoom:
                self.camera = Camera2D(zoom=2)
                self.is_zoom = True
                self.ui_manager.enable()
                self.box_layout.clear()
                self.interface_for_arrangement_of_towers()
            elif button == arcade.MOUSE_BUTTON_RIGHT:
                if self.camera:
                    self.camera.zoom = 1
                    self.is_zoom = False
                    self.ui_manager.disable()

    def on_show_view(self):
        self.window.set_size(1440, 800)
        self.window.center_window()

    def interface_for_arrangement_of_towers(self):
        label = UILabel(
            text="Выберите позицию башни или дорогу:",
            font_size=40,
            text_color=arcade.color.WHITE
        )
        self.box_layout.add(label)

        self.selection_position_panel = UIDropdown(
            options=list(self.tower_positions.keys()),
            default="Северо-западная позиция",
            width=300
        )
        self.box_layout.add(self.selection_position_panel)

        choice_button = UITextureButton(
            texture=self.texture_btn_normal,
            texture_hovered=self.texture_btn_hovered,
            texture_pressed=self.texture_btn_pressed,
            text="Выбрать"
        )
        choice_button.on_click = self.on_choosing_position
        self.box_layout.add(choice_button)

    def interface_for_building_towers(self, building, road):
        self.box_layout.clear()

        if not building:
            if road:
                self.is_barricade = True
                label = UILabel(
                    text="Постройте баррикаду (10 золота)",
                    font_size=30,
                    text_color=arcade.color.WHITE
                )
                self.box_layout.add(label)

                build_button = UITextureButton(
                    texture=self.texture_btn_normal,
                    texture_hovered=self.texture_btn_hovered,
                    texture_pressed=self.texture_btn_pressed,
                    text="Построить"
                )
                build_button.on_click = self.build
                self.box_layout.add(build_button)
            else:
                label = UILabel(
                    text="Постройте башню (Лучник - 20, Катапульта - 30, Баллиста - 25)",
                    font_size=20,
                    text_color=arcade.color.WHITE
                )
                self.box_layout.add(label)

                self.selection_tower_panel = UIDropdown(
                    options=["Лучник", "Катапульта", "Баллиста"],
                    default="Лучник",
                    width=300
                )
                self.box_layout.add(self.selection_tower_panel)

                build_button = UITextureButton(
                    texture=self.texture_btn_normal,
                    texture_hovered=self.texture_btn_hovered,
                    texture_pressed=self.texture_btn_pressed,
                    text="Построить"
                )
                build_button.on_click = self.build
                self.box_layout.add(build_button)
        else:
            if road:
                label = UILabel(
                    text=f"Улучшите баррикаду (40 золота)",
                    font_size=30,
                    text_color=arcade.color.WHITE
                )
                self.box_layout.add(label)

                upgrade_button = UITextureButton(
                    texture=self.texture_btn_normal,
                    texture_hovered=self.texture_btn_hovered,
                    texture_pressed=self.texture_btn_pressed,
                    text="Улучшить"
                )
                if building.level < 3:
                    upgrade_button.on_click = lambda event: self.upgrade(building)
                    self.box_layout.add(upgrade_button)
                else:
                    upgrade_button.disabled()
            else:
                label = UILabel(
                    text=f"Улучшите башню (Лучник - 30, Катапульта - 60, Баллиста - 50)",
                    font_size=20,
                    text_color=arcade.color.WHITE
                )
                self.box_layout.add(label)

                upgrade_button = UITextureButton(
                    texture=self.texture_btn_normal,
                    texture_hovered=self.texture_btn_hovered,
                    texture_pressed=self.texture_btn_pressed,
                    text="Улучшить"
                )
                if building.level < 3:
                    upgrade_button.on_click = lambda event: self.upgrade(building)
                    self.box_layout.add(upgrade_button)
                else:
                    upgrade_button.disabled()

    def on_choosing_position(self, event):
        self.selected_position = self.selection_position_panel.value
        self.selected_position_coords = self.tower_positions[self.selected_position]
        road = "дорога" in self.selected_position
        building = self.get_building(self.selected_position, road)
        self.interface_for_building_towers(building, road)

    def get_building(self, position, road):
        x, y = self.tower_positions[position]
        if not road:
            for tower in self.list_towers:
                if tower.center_x == x and tower.center_y == y:
                    return tower
        else:
            for barricade in self.list_barricades:
                if barricade.center_x == x and barricade.center_y == y:
                    return barricade
        return None

    def build(self, event):
        self.current_building = str(self.selection_tower_panel.value) if not self.is_barricade else "Баррикада"
        if self.gold >= self.cost_towers[self.current_building][0]:
            if self.current_building == "Баррикада":
                barricade = Barricade(*self.selected_position_coords, 1, 50)
                self.list_barricades.append(barricade)
                self.is_barricade = False
            else:
                if self.current_building == "Лучник":
                    tower = Tower(*self.selected_position_coords, 1, type_tower="Archer")
                elif self.current_building == "Катапульта":
                    tower = Tower(*self.selected_position_coords, 1, type_tower="Catapult")
                else:
                    tower = Tower(*self.selected_position_coords, 1, type_tower="Ballista")
                self.list_towers.append(tower)

            self.gold -= self.cost_towers[self.current_building][0]
            self.spent_gold += self.cost_towers[self.current_building][0]
            self.amount_gold.text = f"Золото: {self.gold}"
            self.box_layout.clear()
            self.interface_for_arrangement_of_towers()

    def upgrade(self, building):
        if self.gold >= self.cost_towers[self.current_building][1]:
            building.upgrade()
            self.gold -= self.cost_towers[self.current_building][1]
            self.spent_gold += self.cost_towers[self.current_building][1]
            self.amount_gold.text = f"Золото: {self.gold}"
            self.box_layout.clear()
            self.interface_for_arrangement_of_towers()

    def spawn_enemy(self, type_enemy):
        position = choice(list(self.enemies_position.keys()))
        coordinates = self.enemies_position[position]
        if type_enemy == "militiaman":
            enemy = Militiaman(*coordinates, spawn_side=position)
        elif type_enemy == "lancer":
            enemy = Lancer(*coordinates, spawn_side=position)
        elif type_enemy == "knight":
            enemy = Knight(*coordinates, spawn_side=position)
        else:
            enemy = Ram(*coordinates, spawn_side=position)
        self.list_enemies.append(enemy)


class GameOverView(arcade.View):
    def __init__(self):
        super().__init__()
        self.batch = Batch()
        self.lose_text = arcade.Text("Вы проиграли!", self.window.width / 2, self.window.height / 2,
                                      arcade.color.WHITE, font_size=40, anchor_x="center", batch=self.batch)
        self.space_text = arcade.Text("Нажмите SPACE, чтобы начать заново", self.window.width / 2,
                                      self.window.height / 2 - 50,
                                      arcade.color.WHITE, font_size=20, anchor_x="center", batch=self.batch)

    def on_draw(self):
        self.clear()
        self.batch.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            game_view = GameView()
            game_view.camera = None
            game_view.setup()
            self.window.show_view(game_view)


class GameWinView(arcade.View):
    def __init__(self, game_view, time, count_defeated_enemies, spent_gold):
        super().__init__()
        self.game_view = game_view
        self.batch = Batch()
        self.win_text = arcade.Text("Вы выиграли!", self.window.width / 2, self.window.height / 2 + 100,
                                      arcade.color.WHITE, font_size=40, anchor_x="center", batch=self.batch)
        self.time_text = arcade.Text(f"Время: {int(time)}", self.window.width / 2, self.window.height / 2 + 50,
                                      arcade.color.LIGHT_BLUE, font_size=30, anchor_x="center", batch=self.batch)
        self.count_enemies_text = arcade.Text(f"Количество поверженных врагов: {count_defeated_enemies}",
                                              self.window.width / 2, self.window.height / 2,
                                              arcade.color.LIGHT_RED_OCHRE, font_size=30, anchor_x="center",
                                              batch=self.batch)
        self.spent_gold_text = arcade.Text(f"Потраченное золото: {spent_gold}", self.window.width / 2,
                                           self.window.height / 2 - 50,
                                           arcade.color.YELLOW, font_size=30, anchor_x="center", batch=self.batch)
        self.space_text = arcade.Text("Нажмите SPACE, чтобы выйти из игры", self.window.width / 2,
                                      self.window.height / 2 - 100,
                                      arcade.color.WHITE, font_size=40, anchor_x="center", batch=self.batch)

    def on_draw(self):
        self.clear()
        self.batch.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.window.close()


class PauseView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.batch = Batch()
        self.pause_text = arcade.Text("Пауза", self.window.width / 2, self.window.height / 2,
                                      arcade.color.WHITE, font_size=40, anchor_x="center", batch=self.batch)
        self.space_text = arcade.Text("Нажми SPACE, чтобы продолжить", self.window.width / 2,
                                      self.window.height / 2 - 50,
                                      arcade.color.WHITE, font_size=20, anchor_x="center", batch=self.batch)

    def on_draw(self):
        self.clear()
        self.batch.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.window.show_view(self.game_view)
