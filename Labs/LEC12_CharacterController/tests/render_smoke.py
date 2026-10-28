"""Render actual Pico2D states offscreen and save the three screenshots."""

import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
os.environ['SDL_RENDER_DRIVER'] = 'software'
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pico2d as p
import main as game
import boy
import auto_run


def snapshot(name):
    p.clear_canvas()
    for obj in game.world:
        obj.draw()
    renderer = p.open_canvas.__globals__['renderer']
    surface = p.SDL_CreateRGBSurfaceWithFormat(0, 800, 600, 32, p.SDL_PIXELFORMAT_RGBA32)
    try:
        assert p.SDL_RenderReadPixels(renderer, None, p.SDL_PIXELFORMAT_RGBA32,
                                      surface.contents.pixels, surface.contents.pitch) == 0, p.SDL_GetError()
        assert p.IMG_SavePNG(surface, str(ROOT / 'docs' / name).encode('utf-8')) == 0, p.SDL_GetError()
    finally:
        p.SDL_FreeSurface(surface)
    p.update_canvas()


if __name__ == '__main__':
    (ROOT / 'docs').mkdir(exist_ok=True)
    p.open_canvas(800, 600)
    try:
        assert p.open_canvas.__globals__['renderer'], p.SDL_GetError()
        with patch.object(boy, 'monotonic', return_value=0), patch.object(auto_run, 'monotonic', return_value=0):
            game.reset_world()
            snapshot('preview_idle.png')
            game.boy.handle_event(SimpleNamespace(type=p.SDL_KEYDOWN, key=p.SDLK_a))
            assert game.boy.invincible and game.boy.state == 'AUTORUN'
            snapshot('preview_auto_run.png')
            game.boy.handle_event(SimpleNamespace(type=p.SDL_KEYDOWN, key=p.SDLK_LEFT))
            assert not game.boy.invincible and game.boy.state == 'RUN'
            snapshot('preview_run.png')
            print('PASS: real SDL rendering of IDLE, AUTORUN and RUN; relative asset paths work')
    finally:
        p.close_canvas()
