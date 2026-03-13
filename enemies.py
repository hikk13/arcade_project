import arcade


class Enemy(arcade.Sprite):
    def __init__(self, center_x, center_y, spawn_side):
        super().__init__(center_x=center_x, center_y=center_y)
        self.hp = None
        self.speed = None
        self.damage = None
        self.spawn_side = spawn_side
        self.is_walking = True
        self.is_attacking = False

        self.idle_texture = None
        self.textures = []
        self.texture_change_time = 0
        self.texture_change_delay = 0.4

    def update(self, delta_time: float = 1 / 60):
        if self.is_walking:
            if self.spawn_side == "Запад":
                self.center_x += self.speed * delta_time
            elif self.spawn_side == "Восток":
                self.center_x -= self.speed * delta_time
            elif self.spawn_side == "Север":
                self.center_y -= self.speed * delta_time
            elif self.spawn_side == "Юг":
                self.center_y += self.speed * delta_time

    def update_animation(self, delta_time: float = 1 / 60):
        if self.is_walking:
            self.texture_change_time += delta_time
            if self.texture_change_time >= self.texture_change_delay:
                self.texture_change_time = 0
                if self.texture == self.idle_texture:
                    self.texture = self.textures[0]
                else:
                    self.texture = self.idle_texture
        elif self.is_attacking:
            self.texture_change_time += delta_time
            if self.texture_change_time >= self.texture_change_delay:
                self.texture_change_time = 0
                if self.texture == self.idle_texture:
                    self.texture = self.textures[1]
                else:
                    self.texture = self.idle_texture
        else:
            self.texture = self.idle_texture


class Militiaman(Enemy):
    def __init__(self, center_x, center_y, spawn_side):
        super().__init__(center_x, center_y, spawn_side)
        self.idle_texture = arcade.load_texture("images/enemies/militiaman.png")
        self.texture = self.idle_texture
        self.textures = [
            arcade.load_texture("images/enemies/militiaman_walk.png"),
            arcade.load_texture("images/enemies/militiaman_attack.png")
        ]
        self.hp = 25
        self.speed = 15
        self.damage = 10


class Lancer(Enemy):
    def __init__(self, center_x, center_y, spawn_side):
        super().__init__(center_x, center_y, spawn_side)
        self.idle_texture = arcade.load_texture("images/enemies/lancer.png")
        self.texture = self.idle_texture
        self.textures = [
            arcade.load_texture("images/enemies/lancer_walk.png"),
            arcade.load_texture("images/enemies/lancer_attack.png")
        ]
        self.hp = 50
        self.speed = 15
        self.damage = 15


class Knight(Enemy):
    def __init__(self, center_x, center_y, spawn_side):
        super().__init__(center_x, center_y, spawn_side)
        self.idle_texture = arcade.load_texture("images/enemies/knight.png")
        self.texture = self.idle_texture
        self.textures = [
            arcade.load_texture("images/enemies/knight_walk.png"),
            arcade.load_texture("images/enemies/knight_attack.png")
        ]
        self.hp = 75
        self.speed = 10
        self.damage = 25


class Ram(Enemy):
    def __init__(self, center_x, center_y, spawn_side):
        super().__init__(center_x, center_y, spawn_side)
        self.idle_texture = arcade.load_texture("images/enemies/ram.png")
        self.texture = self.idle_texture
        self.textures = [
            arcade.load_texture("images/enemies/ram_walk.png"),
            arcade.load_texture("images/enemies/ram_attack.png")
        ]
        self.hp = 100
        self.speed = 10
        self.damage = 40