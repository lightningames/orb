# -*- coding: utf-8 -*-
# @Author: lnorb.com
# @Date:   2022-07-09 10:09:47
# @Last Modified by:   lnorb.com
# @Last Modified time: 2022-07-09 10:10:07
from pythonforandroid.recipe import NDKRecipe
from pythonforandroid.toolchain import shutil
from os.path import join
import sh


class Sqlite3Recipe(NDKRecipe):
    version = "3.38.0"
    # Don't forget to change the URL when changing the version
    url = "https://www.sqlite.org/2022/sqlite-amalgamation-3380000.zip"
    generated_libraries = ["sqlite3"]

    def should_build(self, arch):
        return not self.has_libs(arch, "libsqlite3.so")

    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        # Copy the Android make file
        sh.mkdir("-p", join(self.get_build_dir(arch.arch), "jni"))
        shutil.copyfile(
            join(self.get_recipe_dir(), "Android.mk"),
            join(self.get_build_dir(arch.arch), "jni/Android.mk"),
        )

    def build_arch(self, arch, *extra_args):
        super().build_arch(arch)
        # Copy the shared library
        shutil.copyfile(
            join(self.get_build_dir(arch.arch), "libs", arch.arch, "libsqlite3.so"),
            join(self.ctx.get_libs_dir(arch.arch), "libsqlite3.so"),
        )

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        env["NDK_PROJECT_PATH"] = self.get_build_dir(arch.arch)
        env["SQLITE_ENABLE_JSON1"] = "1"
        return env


recipe = Sqlite3Recipe()
