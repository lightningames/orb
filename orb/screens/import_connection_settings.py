# -*- coding: utf-8 -*-
# @Author: lnorb.com
# @Date:   2022-06-30 14:26:36
# @Last Modified by:   lnorb.com
# @Last Modified time: 2022-08-08 12:26:25

from kivymd.uix.screen import MDScreen

import os

from pathlib import Path
from tempfile import mkdtemp

from kivy.app import App
from kivy.config import ConfigParser
from kivymd.uix.screen import MDScreen

from orb.misc.utils import mobile
from orb.misc.decorators import guarded
from orb.misc.utils import get_available_nodes
from orb.dialogs.restart_dialog import RestartDialog


class ImportConnectionSettings(MDScreen):

    connected = False

    lnd_settings_to_copy = [
        "rest_port",
        "tls_certificate",
        "network",
        "protocol",
        "macaroon_admin",
        "type",
        "identity_pubkey",
    ]

    @guarded
    def import_node_settings(self):
        d = mkdtemp()
        p = Path(d) / "orb.ini"
        with p.open("w") as f:
            f.write(self.ids.text_import.text)
        config = ConfigParser()
        config.read(p.as_posix())
        target_config = ConfigParser()
        pk = config["lnd"]["identity_pubkey"]
        app = App.get_running_app()
        app.node_settings["host.hostname"] = config["host"]["hostname"]
        for s in self.lnd_settings_to_copy:
            app.node_settings[f"lnd.{s}"] = config["lnd"][s]
        if mobile:
            app.node_settings["lnd.protocol"] = "rest"

    @guarded
    def connect(self):
        app = App.get_running_app()
        if self.connected:
            RestartDialog(
                title="After exit, please restart Orb to launch new settings."
            ).open()
            return

        error = ""
        try:
            from orb.ln import Ln

            ln = Ln(
                fallback_to_mock=False,
                cache=False,
                use_prefs=False,
                hostname=app.node_settings["host.hostname"],
                protocol=app.node_settings["lnd.protocol"],
                mac_secure=app.node_settings["lnd.macaroon_admin"],
                cert_secure=app.node_settings["lnd.tls_certificate"],
                rest_port=8080,
                grpc_port=10009,
            )

            info = ln.get_info()

            self.ids.connect.text = f"Set {info.identity_pubkey[:5]} as default ..."
            self.connected = True
            self.ids.connect.md_bg_color = (0.2, 0.8, 0.2, 1)
        except Exception as e:
            print(e)
            error = "Error connecting to LND"

        if error:
            self.ids.connect.text = f"Error: {error}"
            self.ids.connect.md_bg_color = (0.8, 0.2, 0.2, 1)
