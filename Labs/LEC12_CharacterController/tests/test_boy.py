import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import boy as boy_module
import auto_run as auto_run_module
from auto_run import AutoRun
from pico2d import SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE, SDLK_a


class BoyStateTests(unittest.TestCase):
    def setUp(self):
        self.now = 0.0
        for module in (boy_module, auto_run_module):
            clock = patch.object(module, 'monotonic', side_effect=lambda: self.now)
            clock.start()
            self.addCleanup(clock.stop)
        canvas = patch.object(boy_module, 'get_canvas_width', return_value=800)
        canvas.start()
        self.addCleanup(canvas.stop)
        image = patch.object(boy_module.Boy, 'image', Mock())
        image.start()
        self.addCleanup(image.stop)
        self.boy = boy_module.Boy()

    def press(self, key, repeat=False):
        self.boy.handle_event(SimpleNamespace(type=SDL_KEYDOWN, key=key, repeat=repeat))

    def release(self, key):
        self.boy.handle_event(SimpleNamespace(type=SDL_KEYUP, key=key))

    def tick(self, now):
        self.now = now
        self.boy.update()

    def test_centered_initial_idle(self):
        self.assertEqual((self.boy.x, self.boy.y, self.boy.state), (400, 90, 'IDLE'))
        self.assertFalse(self.boy.invincible)

    def test_a_enters_real_auto_run_class(self):
        self.press(SDLK_a)
        self.assertIsInstance(self.boy.auto_run, AutoRun)
        self.assertEqual(self.boy.state, AutoRun.NAME)
        self.assertTrue(self.boy.invincible)
        self.assertEqual(self.boy.scale, 1.5)
        self.release(SDLK_a)
        self.tick(0.25)
        self.assertEqual(self.boy.x, 500)  # 400 pixels/s without held keys.

    def test_enlargement_keeps_feet_at_same_height(self):
        self.press(SDLK_a)
        self.boy.draw()
        self.boy.image.clip_draw.assert_called_with(0, 100, 100, 100, 400, 115, 150, 150)

    def test_expanded_bounds_at_entry_and_both_bounces(self):
        self.boy.x = 750
        self.press(SDLK_a)
        self.assertEqual(self.boy.x, 725)
        self.tick(0.25)
        self.assertEqual((self.boy.x, self.boy.direction), (625, -1))
        self.tick(1.75)
        self.assertEqual((self.boy.x, self.boy.direction), (125, 1))

    def test_bounce_exactly_at_right_edge(self):
        self.press(SDLK_a)
        self.tick(0.8125)
        self.assertEqual((self.boy.x, self.boy.direction), (725, -1))

    def test_large_frame_reflects_multiple_edges(self):
        self.press(SDLK_a)
        self.tick(4.9)
        self.assertEqual((self.boy.x, self.boy.direction), (390, -1))

    def test_auto_run_timeout_restores_idle_and_timer(self):
        self.press(SDLK_a)
        self.tick(4.999)
        self.assertEqual(self.boy.state, AutoRun.NAME)
        self.tick(5.0)
        self.assertEqual(self.boy.state, 'IDLE')
        self.assertEqual(self.boy.scale, 1)
        self.assertFalse(self.boy.invincible)
        self.assertEqual(self.boy.idle_started_at, 5.0)
        self.tick(9.999)
        self.assertEqual(self.boy.state, 'IDLE')
        self.tick(10.0)
        self.assertEqual(self.boy.state, 'SLEEP')

    def test_arrows_cancel_auto_run_in_both_directions(self):
        for key, direction in ((SDLK_LEFT, -1), (SDLK_RIGHT, 1)):
            with self.subTest(direction=direction):
                self.now = 0
                self.boy = boy_module.Boy()
                self.press(SDLK_a)
                self.now = 1.0
                self.press(key)
                self.assertEqual((self.boy.state, self.boy.direction), ('RUN', direction))
                self.assertEqual(self.boy.scale, 1)
                self.assertFalse(self.boy.invincible)
                self.tick(1.25)
                self.assertEqual(self.boy.x, 400 + direction * 50)
                self.tick(6.0)
                self.assertEqual(self.boy.state, 'RUN')  # Old AutoRun timer has no effect.
                self.assertEqual(self.boy.x, 50 if direction == -1 else 750)
                self.release(key)
                self.assertEqual(self.boy.state, 'IDLE')

    def test_a_only_works_in_idle_and_repeat_does_not_extend_duration(self):
        self.press(SDLK_a)
        self.now = 2
        self.press(SDLK_a, repeat=True)
        self.assertEqual(self.boy.auto_run.started_at, 0)
        self.tick(5)
        self.press(SDLK_a, repeat=True)
        self.assertEqual(self.boy.state, 'IDLE')
        self.press(SDLK_LEFT)
        self.press(SDLK_a)
        self.assertEqual(self.boy.state, 'RUN')
        self.release(SDLK_LEFT)
        self.tick(10)
        self.press(SDLK_a)
        self.assertEqual(self.boy.state, 'SLEEP')

    def test_sleep_arrows_and_space_still_work(self):
        self.tick(5)
        self.press(SDLK_RIGHT)
        self.assertEqual(self.boy.state, 'RUN')
        self.release(SDLK_RIGHT)
        self.tick(10)
        self.press(SDLK_SPACE)
        self.assertEqual(self.boy.state, 'IDLE')
        self.assertEqual(self.boy.idle_started_at, 10)

    def test_overlapping_keys_and_key_repeats(self):
        self.press(SDLK_LEFT)
        self.press(SDLK_RIGHT)
        self.press(SDLK_LEFT, repeat=True)
        self.assertEqual(self.boy.direction, 1)
        self.release(SDLK_RIGHT)
        self.assertEqual((self.boy.state, self.boy.direction), ('RUN', -1))
        self.release(SDLK_LEFT)
        self.assertEqual(self.boy.state, 'IDLE')

    def test_auto_run_uses_last_facing_direction(self):
        self.press(SDLK_LEFT)
        self.release(SDLK_LEFT)
        self.press(SDLK_a)
        self.tick(0.25)
        self.assertEqual((self.boy.x, self.boy.direction), (300, -1))


if __name__ == '__main__':
    unittest.main()
