from pico2d import (
    load_image, get_canvas_width,
    SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_LEFT, SDLK_RIGHT, SDLK_a,
)
from math import pi
from pathlib import Path
from transitions.extensions import GraphMachine
from time import monotonic

class Boy:
    image = None
    IDLE_TIMEOUT = 5.0
    RUN_SPEED = 200.0  # Pixels per second.
    RUN_FPS = 10.0
    SPRITE_SIZE = 100

    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.scale = 1.0
        self.invincible = False
        self.direction = 1
        self.pressed_keys = []
        self.last_update = monotonic()
        self.machine = GraphMachine(
            model=self,
            states=[
                {'name': 'IDLE', 'on_enter': 'start_idle_timer'},
                {'name': 'RUN', 'on_enter': 'start_run'},
                'SLEEP',
            ],
            transitions=[
                {'trigger': 'start_running', 'source': ['IDLE', 'SLEEP'], 'dest': 'RUN'},
                {'trigger': 'stop_running', 'source': 'RUN', 'dest': 'IDLE'},
                {'trigger': 'fall_asleep', 'source': 'IDLE', 'dest': 'SLEEP'},
                {'trigger': 'wake_up', 'source': 'SLEEP', 'dest': 'IDLE'},
            ],
            initial='IDLE',
            auto_transitions=False,
            graph_engine='mermaid',
            title='Boy State Machine',
        )
        # GraphMachine does not call on_enter for the initial state.
        self.start_idle_timer()
        if Boy.image is None:
            Boy.image = load_image(str(Path(__file__).resolve().with_name('animation_sheet.png')))

    def start_idle_timer(self):
        self.frame = 0
        self.idle_started_at = monotonic()

    def start_run(self):
        self.frame = 0
        self.last_update = monotonic()

    def handle_event(self, event):
        if self.state == 'SLEEP' and event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            self.wake_up()
            return

        if event.type not in (SDL_KEYDOWN, SDL_KEYUP):
            return
        if event.key not in (SDLK_LEFT, SDLK_RIGHT):
            return

        if event.type == SDL_KEYDOWN:
            # Ignore key repeats so the most recently pressed key keeps priority.
            if event.key in self.pressed_keys:
                return
            self.pressed_keys.append(event.key)
            self.direction = 1 if event.key == SDLK_RIGHT else -1
            if self.state in ('IDLE', 'SLEEP'):
                self.start_running()
        elif event.key in self.pressed_keys:
            self.pressed_keys.remove(event.key)
            if self.pressed_keys:
                self.direction = 1 if self.pressed_keys[-1] == SDLK_RIGHT else -1
            elif self.state == 'RUN':
                self.stop_running()

    def horizontal_bounds(self):
        half_width = self.SPRITE_SIZE * self.scale / 2
        canvas_width = get_canvas_width()
        if canvas_width <= 2 * half_width:
            return canvas_width / 2, canvas_width / 2
        return half_width, canvas_width - half_width

    def clamp_to_screen(self):
        left, right = self.horizontal_bounds()
        self.x = max(left, min(right, self.x))

    def update(self):
        now = monotonic()
        elapsed = now - self.last_update
        self.last_update = now

        if self.state == 'RUN':
            self.x += self.direction * self.RUN_SPEED * elapsed
            self.clamp_to_screen()
            self.frame = (self.frame + self.RUN_FPS * elapsed) % 8
        elif self.state == 'IDLE' and now - self.idle_started_at >= self.IDLE_TIMEOUT:
            self.fall_asleep()

    def draw_running(self):
        row = 100 if self.direction == 1 else 0
        size = self.SPRITE_SIZE * self.scale
        # Keep the bottom of the frame at the same height when enlarged.
        draw_y = self.y + (size - self.SPRITE_SIZE) / 2
        self.image.clip_draw(int(self.frame) * 100, row, 100, 100, self.x, draw_y, size, size)

    def draw(self):
        if self.state == 'RUN':
            self.draw_running()
            return
        if self.state == 'SLEEP':
            # Fall backward with the face up; keep the original 100x100 size.
            self.image.clip_composite_draw(
                0, 300 if self.direction == 1 else 200, 100, 100,
                self.direction * pi / 2, '',
                self.x, self.y - 25, 100, 100,
            )
        else:
            row = 300 if self.direction == 1 else 200
            self.image.clip_draw(int(self.frame) * 100, row, 100, 100, self.x, self.y)
