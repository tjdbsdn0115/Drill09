from time import monotonic


class AutoRun:
    """Automatic running state, developed in feature-sized steps."""

    NAME = 'AUTORUN'
    SPEED_MULTIPLIER = 2.0
    SCALE = 1.5

    def __init__(self, boy):
        self.boy = boy
        self.started_at = 0.0

    def enter(self):
        boy = self.boy
        self.started_at = monotonic()
        boy.last_update = self.started_at
        boy.frame = 0
        boy.scale = self.SCALE
        boy.invincible = True
        boy.pressed_keys.clear()
        # The enlarged sprite must fit even when activated near an edge.
        boy.clamp_to_screen()

    def exit(self):
        self.boy.scale = 1.0
        self.boy.invincible = False
        self.boy.clamp_to_screen()

    def update(self, now, elapsed):
        boy = self.boy
        boy.x += boy.direction * boy.RUN_SPEED * self.SPEED_MULTIPLIER * elapsed
        boy.clamp_to_screen()
        boy.frame = (boy.frame + boy.RUN_FPS * self.SPEED_MULTIPLIER * elapsed) % 8

    def draw(self):
        self.boy.draw_running()
