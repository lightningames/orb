# -*- coding: utf-8 -*-
# @Author: lnorb.com
# @Date:   2021-12-15 07:15:28
# @Last Modified by:   lnorb.com
# @Last Modified time: 2022-08-10 08:16:32

from random import choice
from orb.app import App


def get_low_inbound_channel(pk_ignore, chan_ignore, num_sats):
    """
    Pick a channel for sending out sats.
    """
    chans = []
    app = App.get_running_app()
    channels = app.channels
    for chan in channels:
        if chan.remote_pubkey in pk_ignore:
            continue
        if chan.chan_id in chan_ignore:
            continue
        enough_available_outbound = int(num_sats) < chan.local_balance

        more_than_half_outbound = (
            (chan.local_balance - num_sats) / int(chan.capacity)
        ) > chan.balanced_ratio
        good_candidate = enough_available_outbound and more_than_half_outbound
        if good_candidate:
            chans.append(chan)
    if chans:
        return choice(chans).chan_id


def get_low_outbound_channel(pk_ignore, chan_ignore, num_sats, ratio=0.5):
    chans = []
    app = App.get_running_app()
    channels = app.channels
    for chan in channels:
        if chan.remote_pubkey in pk_ignore:
            continue
        if chan.chan_id in chan_ignore:
            continue
        enough_available_inbound = int(num_sats) < chan.local_balance
        more_than_half_inbound = (
            (chan.local_balance - num_sats) / int(chan.capacity)
        ) > chan.balanced_ratio
        good_candidate = enough_available_inbound and more_than_half_inbound
        if good_candidate:
            chans.append(chan)
    if chans:
        chan = choice(chans)
        return chan.chan_id, chan.remote_pubkey
