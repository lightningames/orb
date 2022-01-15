# -*- coding: utf-8 -*-
# @Author: lnorb.com
# @Date:   2022-01-15 13:22:44
# @Last Modified by:   lnorb.com
# @Last Modified time: 2022-01-15 13:40:24
# -*- coding: utf-8 -*-
# @Author: lnorb.com
# @Date:   2021-12-15 07:15:28
# @Last Modiconsumablesfied by:   lnorb.com
# @Last Modified time: 2022-01-15 13:07:26

from traceback import print_exc
from collections import deque
import uuid

from pygments.lexers import CythonLexer

from kivy.app import App
from kivy.clock import (
    Clock,
    _default_time as time,
)  # ok, no better way to use the same clock as kivy, hmm
from kivy.clock import mainthread
from kivy.properties import StringProperty
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.codeinput import CodeInput
from kivy.utils import platform

from orb.store.scripts import Script, save_scripts, load_scripts
from orb.components.popup_drop_shadow import PopupDropShadow
from orb.misc import data_manager


ios = platform == "ios"
MAX_TIME = 1 / 5


class ConsoleFileChooser(PopupDropShadow):

    selected_path = StringProperty("")


class ConsoleScreen(Screen):

    lines = deque()
    player_showing = False
    show_player = False

    def __init__(self, *args, **kwargs):
        super(ConsoleScreen, self).__init__(*args, **kwargs)
        Clock.schedule_interval(self.consume, 0)

    def on_enter(self):
        """
        We have entered the console screen
        """

        @mainthread
        def delayed():
            # when 'output' changes on the console_input
            # then update 'output' on the console_output
            self.ids.console_input.bind(output=self.ids.console_output.setter("output"))
            # retrieve the code stored in the prefs, and set it
            # in the console input

            self.ids.console_input.text = data_manager.data_man.store.get(
                "console_input", {}
            ).get("text", "")
            app = App.get_running_app()
            app.root.ids.app_menu.add_console_menu(cbs=self.ids.console_input)

        delayed()

    def update_output(self, text, last_line):
        if text and text != "\n":
            self.ids.console_output.output = text
        if last_line and last_line != "\n":
            app = App.get_running_app()
            app.root.ids.status_line.ids.line_output.output = last_line

    def consume(self, *args):
        """
        Print to the console's output section.
        Print the last line on the status line.
        """
        app = App.get_running_app()
        while app.consumables and time() < (Clock.get_time() + MAX_TIME):
            text = app.consumables.popleft()
            # make sure we have something to print
            if text:
                # make sure it's a string
                text = str(text)
                # split up the output into lines
                text_lines = text.split("\n")
                if text_lines:
                    for line in text_lines:
                        if line:
                            self.lines.append(line)
                    for _ in range(max(0, len(self.lines) - 100)):
                        self.lines.popleft()
                    last_line = text_lines[-1]
                self.update_output("\n".join(self.lines), last_line)


class InstallScript(Popup):
    pass


class DeleteScript(Popup):
    pass


class ConsoleInput(CodeInput):

    output = StringProperty("")

    def __init__(self, *args, **kwargs):
        super(ConsoleInput, self).__init__(
            style_name="monokai", lexer=CythonLexer(), *args, **kwargs
        )

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            if data_manager.data_man.menu_visible:
                return False
        return super(ConsoleInput, self).on_touch_down(touch)

    def exec(self, text):
        try:
            exec(text)
        except:
            print_exc()

    def run(self, *_):
        self.exec(self.text)

    def open_file(self, *_):
        dialog = ConsoleFileChooser()
        dialog.open()

        def do_open(widget, path):
            print(f"opening {path}")
            self.text = open(path).read()

        dialog.bind(selected_path=do_open)

    def install(self, *_):
        inst = InstallScript()
        inst.open()

        def do_install(_, *__):
            script_name = ">".join(
                x.strip() for x in inst.ids.script_name.text.split(">")
            )
            code = self.text
            scripts = load_scripts()
            existing = next(
                iter([x for x in scripts if scripts[x].menu == script_name]), None
            )
            if existing:
                scripts[existing.uuid].code = code
            else:

                uid = str(uuid.uuid4())
                scripts[uid] = Script(code=code, menu=script_name, uuid=uid)

            save_scripts()
            app = App.get_running_app()
            app.root.ids.app_menu.populate_scripts()
            inst.dismiss()

        inst.ids.install.bind(on_release=do_install)
        app = App.get_running_app()
        app.root.ids.app_menu.close_all()

    def delete(self, *_):
        inst = LoadScript()

        try:
            sc = data_manager.data_man.store.get("scripts")
        except:
            pass

        def do_delete(button, *args):
            sc = data_manager.data_man.store.get("scripts", {})
            del sc[button.text]
            data_manager.data_man.store.put("scripts", **sc)
            app = App.get_running_app()
            app.root.ids.app_menu.populate_scripts()
            inst.dismiss()

        for name in sc:
            button = Button(text=name, size_hint=(None, None), size=(480, 40))
            button.bind(on_release=do_delete)
            inst.ids.grid.add_widget(button)

        inst.open()
        app = App.get_running_app()
        app.root.ids.app_menu.close_all()

    def clear_input(self, *_):
        self.text = ""

    def clear_output(self, *_):
        self.output = ""

    def reset_split_size(self, *_):

        data_manager.data_man.store.put(
            "console", input_height=None, output_height=None
        )

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        meta = "meta" in modifiers
        direction = (
            keycode[1]
            if keycode and keycode[1] in ("left", "right", "up", "down")
            else False
        )
        if meta and direction:
            if direction == "left":
                line = self.text.split("\n")[self.cursor_row]
                for i, c in enumerate(line, 1):
                    if c not in (" ", "\t"):
                        self._cursor = (i, self._cursor[1])
                        break
            elif direction == "right":
                line = self.text.split("\n")[self.cursor_row]
                self._cursor = (len(line) - 1, self._cursor[1])

        if text != "\u0135":
            to_save = self.text + (text or "")
            do_eval = keycode[1] == "enter" and self.selection_text

            data_manager.data_man.store.put("console_input", text=to_save)
            if do_eval:
                self.exec(self.selection_text)
                return True
        return super(ConsoleInput, self).keyboard_on_key_down(
            window, keycode, text, modifiers
        )


class ConsoleOutput(TextInput):
    output = StringProperty("")

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            if data_manager.data_man.menu_visible:
                return False
        return super(ConsoleOutput, self).on_touch_down(touch)
