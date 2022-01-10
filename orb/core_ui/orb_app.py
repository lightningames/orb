# -*- coding: utf-8 -*-
# @Author: lnorb.com
# @Date:   2021-12-15 07:15:28
# @Last Modified by:   lnorb.com
# @Last Modified time: 2022-01-10 14:42:16

import os
import sys
import json
from pathlib import Path
from traceback import print_exc
from importlib import __import__
from os.path import join
from glob import glob

from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.effects import stiffscroll
from kivy.utils import platform
from kivy.core.window import Window
from kivy.utils import platform

from orb.misc.monkey_patch import do_monkey_patching
from orb.misc.conf_defaults import set_conf_defaults
from orb.audio.audio_manager import audio_manager
from orb.misc.decorators import guarded
from orb.core_ui.main_layout import MainLayout
from orb.misc.ui_actions import console_output
from orb.misc.utils import pref
from orb.misc.plugin import Plugin

import data_manager

ios = platform == "ios"

sys.path.append("orb/lnd/grpc_generate")
sys.path.append("orb/lnd")

if not ios:
    sys.path.append(os.path.join("user", "scripts"))


do_monkey_patching()
is_dev = "main.py" in sys.argv[0]


class OrbApp(MDApp):
    title = "Orb"

    def get_application_config(self, defaultpath=f"{os.getcwd()}/orb.ini"):
        if platform == "android":
            defaultpath = "/sdcard/.%(appname)s.ini"
        elif platform == "ios":
            defaultpath = "~/Documents/%(appname)s.ini"
        elif platform == "win":
            defaultpath = defaultpath.replace("/", "//")
        path = os.path.expanduser(defaultpath) % {
            "appname": self.name,
            "appdir": self.directory,
        }
        return path

    def load_kvs(self):
        for path in [str(x) for x in Path(".").rglob("*.kv")]:
            if any(x in path for x in ["kivy_garden", "tutes/", "dist/", "user/"]):
                continue
            if "orb.kv" in path:
                continue
            print(f"Loading: {path}")
            Builder.load_file(path)
        # if not is_dev:
        # Builder.load_file("kivy_garden/contextmenu/app_menu.kv")
        # Builder.load_file("kivy_garden/contextmenu/context_menu.kv")

    def save_user_scripts(self):
        """
        Load the scripts from 'user_scripts.json' and save the
        scripts in the users's user_data_dir.
        """

        if os.path.exists("user_scripts.json"):
            with open("user_scripts.json") as f:
                user_scripts = json.loads(f.read())
                scripts_dir = os.path.join(self.user_data_dir, "scripts")
                if not os.path.isdir(scripts_dir):
                    os.mkdir(scripts_dir)
                for path in user_scripts:
                    dest = os.path.join(
                        self.user_data_dir, "scripts", os.path.basename(path)
                    )
                    with open(dest, "w") as f:
                        f.write(user_scripts[path])

    def load_user_scripts(self):
        scripts_dir = os.path.join(self.user_data_dir, "scripts")
        plugins = {}
        for plugin_file_path in glob(os.path.join(scripts_dir, "*.py")):
            plugin_module_name = os.path.basename(os.path.splitext(plugin_file_path)[0])
            try:
                plugins[plugin_module_name] = __import__(plugin_module_name)
            except:
                print_exc()
                print(f"Unable to load {plugin_module_name}")

        for cls in Plugin.__subclasses__():
            print(f"Loading plugin: {cls.__name__} (from {cls.__module__})")
            plugin_instance = cls()
            plugin_instance.install(
                script_name=f"{cls.__module__}.py", class_name=cls.__name__
            )
            if plugin_instance.autorun:
                plugin_instance.main()

    def on_stop(self):
        from orb.logic import thread_manager

        thread_manager.thread_manager.stop_threads()

    def on_start(self):
        sys.path.append(os.path.join(self.user_data_dir, "scripts"))
        audio_manager.set_volume()
        self.save_user_scripts()
        self.load_user_scripts()

        _write = sys.stdout.write

        def write(*args):
            content = " ".join(args)
            _write(content)
            console_output(content)

        sys.stdout.write = write

    def on_pause(self):
        # Here you can save data if needed
        return True

    def on_resume(self):
        # Here you can check if any data needs replacing (usually nothing)
        pass

    def build(self):
        """
        Main build method for the app.
        """
        data_manager.DataManager.ensure_cert()
        self.load_kvs()
        data_manager.data_man = data_manager.DataManager(config=self.config)
        window_sizes = Window.size

        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = self.config["display"]["primary_palette"]
        self.icon = "orb.png"
        self.main_layout = MainLayout()
        return self.main_layout

    def build_config(self, config):
        """
        Default config values.
        """
        set_conf_defaults(config)

    def build_settings(self, settings):
        """
        Configuration screen for the app.
        """
        settings.add_json_panel("Orb", self.config, filename="orb/misc/settings.json")

    def on_config_change(self, config, section, key, value):
        """
        What to do when a config value changes. TODO: needs fixing.
        Currently we'd end up with multiple LND instances for example?
        Simply not an option.
        """
        if f"{section}.{key}" == "audio.volume":
            audio_manager.set_volume()
        elif key == "tls_certificate":
            data_manager.DataManager.save_cert(value)
        self.main_layout.do_layout()

    @guarded
    def run(self, *args):
        super(OrbApp, self).run(*args)
