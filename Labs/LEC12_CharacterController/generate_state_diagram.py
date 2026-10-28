"""Create the lecture-style diagram as PNG, SVG and Mermaid source.

Optional dependency: python -m pip install Pillow
Run this file from any working directory. Korean labels use Malgun Gothic.
"""

import argparse
from math import atan2, cos, sin, pi
from pathlib import Path
from unittest.mock import patch
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont

from boy import Boy

WIDTH, HEIGHT = 1600, 1100
SUPERSAMPLE = 2
INK = '#222222'
ARROW = '#d83b1e'
ROOT = Path(__file__).resolve().parent


def generate(font_path):
    out = ROOT / 'docs'
    out.mkdir(exist_ok=True)
    canvas = Image.new('RGB', (WIDTH * SUPERSAMPLE, HEIGHT * SUPERSAMPLE), 'white')
    draw = ImageDraw.Draw(canvas)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
           '<rect width="100%" height="100%" fill="white"/>']

    def text(x, y, value, size=25, color=INK, anchor='mm'):
        font = ImageFont.truetype(str(font_path), size * SUPERSAMPLE)
        draw.multiline_text((x * SUPERSAMPLE, y * SUPERSAMPLE), value, font=font,
                            fill=color, anchor=anchor, align='center', spacing=10)
        lines = value.split('\n')
        svg_anchor = 'start' if anchor.startswith('l') else 'middle'
        first_y = y - (len(lines) - 1) * (size + 5) / 2
        for i, line in enumerate(lines):
            svg.append(f'<text x="{x}" y="{first_y + i * (size + 5)}" text-anchor="{svg_anchor}" '
                       f'dominant-baseline="central" font-family="Malgun Gothic, sans-serif" '
                       f'font-size="{size}" fill="{color}">{escape(line)}</text>')

    def line(points, color=INK, width=2):
        draw.line([(round(x * SUPERSAMPLE), round(y * SUPERSAMPLE)) for x, y in points],
                  fill=color, width=width * SUPERSAMPLE)
        coordinates = ' '.join(f'{x:.2f},{y:.2f}' for x, y in points)
        svg.append(f'<polyline points="{coordinates}" fill="none" stroke="{color}" stroke-width="{width}"/>')

    def arrow(points, color=ARROW):
        line(points, color, 3)
        x, y = points[-1]
        dx, dy = x - points[-2][0], y - points[-2][1]
        angle = atan2(dy, dx)
        head = [(x, y), (x - 15 * cos(angle - pi / 7), y - 15 * sin(angle - pi / 7)),
                (x - 15 * cos(angle + pi / 7), y - 15 * sin(angle + pi / 7))]
        draw.polygon([(a * SUPERSAMPLE, b * SUPERSAMPLE) for a, b in head], fill=color)
        svg.append('<polygon points="' + ' '.join(f'{a:.2f},{b:.2f}' for a, b in head) + f'" fill="{color}"/>')

    def curve(p0, p1, p2, p3):
        points = []
        for i in range(101):
            t = i / 100
            points.append(tuple((1-t)**3*p0[j] + 3*(1-t)**2*t*p1[j] +
                                3*(1-t)*t*t*p2[j] + t**3*p3[j] for j in (0, 1)))
        arrow(points)

    def node(cx, cy, rx, ry, title, detail=''):
        box = (cx-rx, cy-ry, cx+rx, cy+ry)
        draw.ellipse(tuple(v * SUPERSAMPLE for v in box), fill='white', outline=INK, width=2 * SUPERSAMPLE)
        svg.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="white" stroke="{INK}" stroke-width="2"/>')
        text(cx, cy - (28 if detail else 0), title, 33)
        if detail:
            text(cx, cy + 26, detail, 21)

    text(55, 60, 'Drill09 | 소년 상태 다이어그램', 40, anchor='lm')
    line([(45, 108), (1555, 108)], '#1c9fc9', 3)

    # Curves follow the lecture's oval states and red event arrows.
    curve((225, 369), (230, 145), (1235, 145), (1245, 369))
    text(735, 163, '← / → DOWN  (SLEEP → RUN)', 25)
    curve((655, 371), (600, 270), (365, 270), (305, 371))
    text(480, 280, '5초 경과 / TIME_OUT', 24)
    arrow([(380, 450), (580, 450)])
    text(480, 423, 'SPACE DOWN', 23)
    curve((780, 387), (885, 285), (1030, 285), (1130, 387))
    text(956, 282, '← / → DOWN', 24)
    curve((1130, 513), (1040, 620), (880, 620), (780, 513))
    text(960, 608, '모든 방향키 UP', 24)
    curve((610, 515), (490, 610), (490, 720), (580, 770))
    text(435, 650, "'A' DOWN", 27)
    arrow([(740, 735), (740, 531)])
    text(845, 677, '5초 경과\nTIME_OUT', 23)
    curve((850, 810), (1115, 870), (1360, 750), (1260, 531))
    text(1400, 805, '← / → DOWN\n무적 런 취소', 25)

    draw.ellipse((690 * SUPERSAMPLE, 313 * SUPERSAMPLE, 710 * SUPERSAMPLE, 333 * SUPERSAMPLE), fill=INK)
    svg.append('<circle cx="700" cy="323" r="10" fill="#222222"/>')
    arrow([(700, 333), (700, 365)], INK)
    node(260, 450, 120, 85, 'SLEEP')
    node(700, 450, 120, 85, 'IDLE')
    node(1210, 450, 120, 85, 'RUN')
    node(700, 820, 160, 90, 'AutoRun', '자동 이동 · 무적')
    text(700, 950, '좌우 끝에서 방향 반전 (AutoRun 상태 유지)', 25)
    line([(65, 1000), (1535, 1000)], '#dddddd', 2)
    text(800, 1030, 'RUN: 200 px/s · 100×100   |   AutoRun: 400 px/s · 150×150', 24)
    text(800, 1070, 'IDLE에 돌아올 때마다 5초 타이머 재시작 · AutoRun 종료 시 크기·속도·무적 해제', 21)
    canvas.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS).save(out / 'state_diagram.png')
    svg.append('</svg>')
    (out / 'state_diagram.svg').write_text('\n'.join(svg), encoding='utf-8')

    # Export the actual GraphMachine transitions, rather than a separate list.
    labels = {
        'start_running': 'LEFT / RIGHT DOWN',
        'stop_running': 'All arrow keys UP',
        'start_auto_run': 'A DOWN',
        'finish_auto_run': '5 seconds',
        'fall_asleep': '5 seconds in IDLE',
        'wake_up': 'SPACE DOWN',
    }
    with patch.object(Boy, 'image', object()):
        boy = Boy()
    mermaid = ['stateDiagram-v2', '    direction LR', '    state "AutoRun" as AUTORUN', '    [*] --> IDLE']
    for trigger, event in boy.machine.events.items():
        for transitions in event.transitions.values():
            for transition in transitions:
                mermaid.append(f'    {transition.source} --> {transition.dest}: {labels[trigger]}')
    mermaid.extend([
        '    IDLE: Restart idle timer on entry',
        '    RUN: Manual movement, normal speed and size',
        '    AUTORUN: Invincible, speed x2, size x1.5',
        '    AUTORUN: Reverse direction at screen edges',
    ])
    (out / 'state_diagram.mmd').write_text('\n'.join(mermaid) + '\n', encoding='utf-8')
    print(f'Saved PNG, SVG and Mermaid to {out}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--font', type=Path, default=Path('C:/Windows/Fonts/malgun.ttf'))
    generate(parser.parse_args().font)
