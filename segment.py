from kivy.uix.widget import Widget
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line
from kivy.graphics.vertex_instructions import Ellipse
from lerp import lerp_2d
from math import ceil
from colors import *


class Segment(Widget):
    def __init__(self, points, width, cap, amount=0, color=None, *args, **kwargs):
        super(Segment, self).__init__(*args, **kwargs)
        self.amount = amount
        self.d = 3
        self.r = self.d / 2
        with self.canvas:
            self.color = Color(*color)
            self.line = Line(points=points, width=width, cap=cap)
            Color(*BRIGHT_GREEN)
            self.e = [
                Ellipse(pos=[0, 0], size=[self.d, self.d])
                for _ in range(ceil(self.amount / 1e6))
            ]

    def update_rect(self, amount=0):
        a = lerp_2d(self.line.points[:2], self.line.points[2:], 0.02)
        b = lerp_2d(self.line.points[:2], self.line.points[2:], 0.98)
        n = ceil(amount / 1e6)
        # if n > len(self.e):
        #     self.e.append(Ellipse(pos=[0, 0], size=[self.d, self.d]))
        for i, e in enumerate(self.e):
            e.pos = lerp_2d(
                [a[0] - self.r, a[1] - self.r],
                [b[0] - self.r, b[1] - self.r],
                i / len(self.e),
            )
