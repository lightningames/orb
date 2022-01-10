# -*- coding: utf-8 -*-
# @Author: lnorb.com
# @Date:   2021-12-15 07:15:28
# @Last Modified by:   lnorb.com
# @Last Modified time: 2022-01-10 08:56:57

import base64
import time
from threading import Thread

from kivy.clock import mainthread
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.clock import mainthread

from orb.lnd import Lnd
from orb.misc.prefs import is_rest


class FocusTextInput(TextInput):
    def on_touch_down(self, touch):
        import data_manager

        if self.collide_point(*touch.pos):
            if data_manager.data_man.menu_visible:
                return False
        return super(FocusTextInput, self).on_touch_down(touch)


class MailScreen(Screen):
    def on_enter(self):
        self.get_mail()
        self.ids.contact_list.clear_widgets()
        self.ids.contact_list.add_widget(Label(text="Joe"))

    def get_mail(self):
        @mainthread
        def update(text):
            self.ids.input.text = text

        def func():
            text = ""
            for invoice in Lnd().list_invoices().invoices:
                if invoice.settled:
                    htlc_records = [
                        htlc.custom_records
                        for htlc in invoice.htlcs
                        if htlc.custom_records
                    ]
                    if htlc_records:
                        for r in htlc_records:
                            keysend = r.get("34349334" if is_rest() else 34349334, "")
                            if keysend:
                                if is_rest():
                                    msg = base64.b64decode(keysend)
                                else:
                                    msg = str(keysend).strip("b'")
                                    try:
                                        msg = keysend.decode()
                                    except UnicodeDecodeError:
                                        pass
                                if msg:
                                    text += f"{time.ctime(invoice.settle_date)}:\n\n"
                                    text += f"{msg}\n\n"
            update(text)

        update("fetching...")
        Thread(target=func).start()
