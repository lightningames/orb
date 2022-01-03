# -*- coding: utf-8 -*-
# @Author: lnorb.com
# @Date:   2021-12-15 07:15:28
# @Last Modified by:   lnorb.com
# @Last Modified time: 2022-01-03 13:44:22

from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line
from kivy.animation import Animation

from orb.math.Vector import Vector


class SentReceivedWidget(Widget):
    channel = ObjectProperty(None)

    def __init__(self, channel, *args, **kwargs):
        super(SentReceivedWidget, self).__init__(*args, **kwargs)
        from orb.store import model

        self.channel = channel
        c = self.channel

        skip = False
        try:
            model.FowardEvent().select()
        except:
            skip = True

        if skip:
            self.received = None
            self.sent = None
        else:
            self.received = sum(
                [
                    x.fee
                    for x in model.FowardEvent()
                    .select()
                    .where(model.FowardEvent.chan_id_in == str(c.chan_id))
                ]
            )
            self.sent = sum(
                [
                    x.fee
                    for x in model.FowardEvent()
                    .select()
                    .where(model.FowardEvent.chan_id_out == str(c.chan_id))
                ]
            )
        alpha = 0.5
        with self.canvas:
            Color(*[0.5, 1, 0.5, alpha])
            self.lines = []
            for i in range(int(self.sent / 1_000)):
                self.lines.append(Line(circle=(0, 0, 0, 0, 0), width=1, cap="none"))
            Color(*[0.5, 0.5, 1, alpha])
            for i in range(int(self.received / 100_000)):
                self.lines.append(Line(circle=(0, 0, 0, 0, 0), width=3, cap="none"))

    def anim_to_pos(self, i, r):
        for rr, line in enumerate(self.lines):
            line.circle = (0, 0, r + 100 + (rr * 10), (i * 360) - 2, (i * 360) + 2)
