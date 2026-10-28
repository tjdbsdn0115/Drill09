from time import monotonic


class AutoRun:
    """Automatic running state, developed in feature-sized steps."""

    NAME = 'AUTORUN'

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
        pass

    def draw(self):
        self.boy.draw_running()
