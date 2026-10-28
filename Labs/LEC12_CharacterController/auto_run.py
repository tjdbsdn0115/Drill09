from time import monotonic


class AutoRun:
    """Automatic running state, developed in feature-sized steps."""

    NAME = 'AUTORUN'
    SPEED_MULTIPLIER = 2.0

    def __init__(self, boy):
        self.boy = boy
        self.started_at = 0.0

    def enter(self):
        boy = self.boy
        self.started_at = monotonic()
        boy.last_update = self.started_at
        boy.frame = 0
        boy.pressed_keys.clear()

    def exit(self):
        pass

    def update(self, now, elapsed):
        boy = self.boy
        boy.x += boy.direction * boy.RUN_SPEED * self.SPEED_MULTIPLIER * elapsed
        boy.clamp_to_screen()
        boy.frame = (boy.frame + boy.RUN_FPS * self.SPEED_MULTIPLIER * elapsed) % 8

    def draw(self):
        self.boy.draw_running()
