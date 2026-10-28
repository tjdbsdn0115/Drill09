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
        left, right = boy.horizontal_bounds()
        if left == right:
            boy.x = left
        else:
            boy.x += boy.direction * boy.RUN_SPEED * self.SPEED_MULTIPLIER * elapsed
            # Reflect overshoot so even a long frame stays inside the screen.
            while boy.x < left or boy.x > right:
                if boy.x > right:
                    boy.x = 2 * right - boy.x
                    boy.direction = -1
                elif boy.x < left:
                    boy.x = 2 * left - boy.x
                    boy.direction = 1
            if boy.x >= right:
                boy.direction = -1
            elif boy.x <= left:
                boy.direction = 1

        boy.frame = (boy.frame + boy.RUN_FPS * self.SPEED_MULTIPLIER * elapsed) % 8

    def draw(self):
        self.boy.draw_running()
