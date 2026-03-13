import arcade
import math


class Tower(arcade.Sprite):
    def __init__(self, center_x, center_y, level, type_tower):
        super().__init__(center_x=center_x, center_y=center_y)
        self.texture = arcade.load_texture("images/towers/tower_level1.png")
        self.level = level
        self.count_level = 2
        self.damage = 5 * level
        self.range = 5 * level
        self.type = type_tower

    def update(self, delta_time: float = 1 / 60):
        if self.level == 2 and self.count_level == 2:
            self.texture = arcade.load_texture("images/towers/tower_level2.png")
            self.count_level += 1
        elif self.level == 3 and self.count_level == 3:
            self.texture = arcade.load_texture("images/towers/tower_level3.png")
            self.count_level += 1


class Barrier(arcade.Sprite):
    def __init__(self, center_x, center_y, hp):
        super().__init__(center_x=center_x, center_y=center_y)
        self.hp = hp
        self.full_hp = self.hp


class Castle(Barrier):
    def __init__(self, center_x, center_y, hp):
        super().__init__(center_x, center_y, hp)
        self.texture = arcade.load_texture("images/towers/castle.png")


class Barricade(Barrier):
    def __init__(self, center_x, center_y, level, hp):
        super().__init__(center_x, center_y, hp)
        self.texture = arcade.load_texture("images/towers/barricade_level1.png")
        self.level = level
        self.hp *= level
        self.count_level = 2

    def update(self, delta_time: float = 1 / 60):
        if self.level == 2 and self.count_level == 2:
            self.texture = arcade.load_texture("images/towers/barricade_level2.png")
            self.hp = self.full_hp * self.level
            self.count_level += 1
        elif self.level == 3 and self.count_level == 3:
            self.texture = arcade.load_texture("images/towers/barricade_level3.png")
            self.hp = self.full_hp * self.level
            self.count_level += 1


class Gate(Barrier):
    def __init__(self, center_x, center_y, hp):
        super().__init__(center_x, center_y, hp)
        self.texture = arcade.load_texture("images/towers/gate.png")


class Bullet(arcade.Sprite):
    def __init__(self, start_x, start_y, target_x, target_y, speed, damage):
        super().__init__()
        self.center_x = start_x
        self.center_y = start_y
        self.speed = speed
        self.damage = damage

        x_diff = target_x - start_x
        y_diff = target_y - start_y
        angle = math.atan2(y_diff, x_diff)

        self.change_x = math.cos(angle) * speed
        self.change_y = math.sin(angle) * speed

        angle = math.degrees(angle)
        self.angle = -(angle - 90) if 90 < angle < 180 else abs(angle - 90)

    def update(self, delta_time: float = 1 / 60):
        ...



class Arrow(Bullet):
    def __init__(self, start_x, start_y, target_x, target_y, speed, damage):
        super().__init__(start_x, start_y, target_x, target_y, speed, damage)
        self.texture = arcade.load_texture("images/towers/arrow.png")


class Bolt(Bullet):
    def __init__(self, start_x, start_y, target_x, target_y, speed, damage):
        super().__init__(start_x, start_y, target_x, target_y, speed, damage)
        self.texture = arcade.load_texture("images/towers/bolt.png")

class Boulder(Bullet):
    def __init__(self, start_x, start_y, target_x, target_y, speed, damage):
        super().__init__(start_x, start_y, target_x, target_y, speed, damage)
        self.texture = arcade.load_texture("images/towers/boulder.png")
