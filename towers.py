import arcade
import math


class Tower(arcade.Sprite):
    def __init__(self, center_x, center_y, level, type_tower):
        super().__init__(center_x=center_x, center_y=center_y)
        self.texture = arcade.load_texture("images/towers/tower_level1.png")
        self.level = level
        self.shot_timer = 0
        self.type_tower = type_tower

        if self.type_tower == "Archer":
            self.damage = 15
            self.speed = 40
            self.firing_range = 150
            self.interval = 3.0
        elif self.type_tower == "Catapult":
            self.damage = 25
            self.speed = 25
            self.firing_range = 200
            self.interval = 4.5
        else:
            self.damage = 20
            self.speed = 30
            self.firing_range = 200
            self.interval = 4.2

    def upgrade(self):
        if self.level != 3:
            if self.level == 1:
                self.texture = arcade.load_texture("images/towers/tower_level2.png")
            else:
                self.texture = arcade.load_texture("images/towers/tower_level3.png")

            self.level += 1
            self.damage += 5
            self.speed *= self.level
            self.firing_range += 25
            self.interval /= self.level


class Bullet(arcade.Sprite):
    def __init__(self, filename, tower, target):
        super().__init__(filename)
        self.tower = tower
        self.center_x = tower.center_x
        self.center_y = tower.center_y
        self.speed = tower.speed
        self.damage = tower.damage
        self.firing_range = tower.firing_range

        x_diff = target.center_x - self.center_x
        y_diff = target.center_y - self.center_y
        angle = math.atan2(y_diff, x_diff)

        self.change_x = math.cos(angle) * self.speed
        self.change_y = math.sin(angle) * self.speed

        angle = math.degrees(angle)
        self.angle = -abs(angle - 225) if 180 < angle < 90 else abs(angle - 225)

    def update(self, delta_time: float = 1 / 60):
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time


class Barrier(arcade.Sprite):
    def __init__(self, filename, center_x, center_y, hp):
        super().__init__(filename, center_x=center_x, center_y=center_y)
        self.hp = hp
        self.full_hp = self.hp


class Barricade(Barrier):
    def __init__(self, center_x, center_y, level, hp):
        super().__init__(filename=None, center_x=center_x, center_y=center_y, hp=hp)
        self.texture = arcade.load_texture("images/towers/barricade_level1.png")
        self.level = level
        self.hp *= level

    def upgrade(self):
        if self.level != 3:
            if self.level == 1:
                self.texture = arcade.load_texture("images/towers/barricade_level2.png")
            else:
                self.texture = arcade.load_texture("images/towers/barricade_level3.png")

            self.level += 1
            self.hp = self.full_hp * self.level
