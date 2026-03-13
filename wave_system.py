class WaveManager:
    def __init__(self, waves, spawn_enemy):
        self.waves = waves
        self.spawn_enemy = spawn_enemy
        self.count_waves = 0
        self.current_wave = None
        self.spawn_timer = 0
        self.spawn_delay = 1
        self.queue_enemies = []
        self.wave_active = False

    def start_wave(self):
        if self.count_waves >= len(self.waves):
            return

        self.current_wave = self.waves[self.count_waves]
        self.count_waves += 1

        for part_wave in self.current_wave:
            for _ in range(part_wave["count"]):
                self.queue_enemies.append(part_wave["type_enemy"])

        self.wave_active = True

    def stop_wave(self):
        self.wave_active = False

    def update(self, delta_time):
        if not self.wave_active or not self.queue_enemies:
            return

        self.spawn_timer += delta_time
        if self.spawn_timer >= self.spawn_delay:
            self.spawn_timer = 0
            type_enemy = self.queue_enemies.pop(0)
            self.spawn_enemy(type_enemy)

        if not self.queue_enemies:
            self.stop_wave()