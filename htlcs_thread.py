from munch import Munch
import json
import threading
from time import sleep
from traceback import print_exc

import data_manager
from htlc import Htlc


class HTLCsThread(threading.Thread):
    def __init__(self, inst, *args, **kwargs):
        super(HTLCsThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()
        self.inst = inst

    def run(self):
        rest = False
        while not self.stopped():
            try:
                lnd = data_manager.data_man.lnd
                it = lnd.get_htlc_events()
                if rest:
                    it = it.iter_lines()
                for e in it:
                    if self.stopped():
                        return
                    self.inst.update_rect()
                    if rest:
                        e = Munch.fromDict(json.loads(e)["result"])
                    for cid in self.inst.cn:
                        chans = [
                            e.outgoing_channel_id
                            if hasattr(e, "outgoing_channel_id")
                            else None,
                            e.incoming_channel_id
                            if hasattr(e, "incoming_channel_id")
                            else None,
                        ]
                        if self.inst.cn[cid].l.channel.chan_id in chans:
                            self.inst.cn[cid].l.anim_htlc(Htlc(lnd, e))
            except:
                print("Exception getting HTLCs - let's sleep")
                print_exc()
                sleep(10)

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()