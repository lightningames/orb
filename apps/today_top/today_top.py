# -*- coding: utf-8 -*-
# @Author: lnorb.com
# @Date:   2022-01-03 11:27:01
# @Last Modified by:   lnorb.com
# @Last Modified time: 2022-08-07 12:16:06

from collections import defaultdict

from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.metrics import dp

from orb.store import model
from orb.lnd import Ln

from orb.misc.plugin import Plugin


class TodayTop(Plugin):
    def main(self):
        ln, today_totals = Ln(), defaultdict(int)
        channels = {c.chan_id: c for c in ln.get_channels()}
        for e in (
            model.ForwardEvent().select().where(model.ForwardEvent.today() == True)
        ):
            today_totals[e.chan_id_out] += e.fee

        Popup(
            title="Today Top Routing",
            content=Label(
                text="\n".join(
                    [
                        f"{ln.get_node_alias(channels.get(chan_id).remote_pubkey)}: S{total:,}"
                        for chan_id, total in sorted(
                            today_totals.items(), key=lambda x: x[1], reverse=True
                        )
                        if channels.get(chan_id) and total
                    ]
                )
            ),
            size_hint=(None, None),
            size=(dp(300), dp(300)),
            background_color=[0.6, 0.6, 0.8, 0.9],
            overlay_color=[0, 0, 0, 0],
        ).open()
