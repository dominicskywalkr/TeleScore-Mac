import os
import plistlib
import subprocess
import sys
import tempfile

from cx_Freeze import Executable, setup


ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
LICENSE = os.path.join(ROOT_PATH, "LICENSE")
SOURCE_PATH = os.path.join(ROOT_PATH, "src")
ICON_PATH = os.path.join(SOURCE_PATH, "resources", "icon.ico")
MACOS_ICON_PATH = os.path.join(ROOT_PATH, "TeleScore icon.icon")
MACOS_ICON_NAME = "TeleScore icon"
PACKAGES = ["PyQt6", "requests", "pynput", "src"]
INCLUDE_FILES = [
    (os.path.join(SOURCE_PATH, "theme"), os.path.join("src", "theme")),
    (os.path.join(SOURCE_PATH, "resources"), os.path.join("src", "resources")),
    (LICENSE, "LICENSE"),
]


def collect_ui_files():
    ui_files = []
    for directory, _, file_names in os.walk(SOURCE_PATH):
        for file_name in file_names:
            if file_name.endswith(".ui"):
                source_file = os.path.join(directory, file_name)
                destination = os.path.relpath(source_file, ROOT_PATH)
                ui_files.append((source_file, destination))
    return ui_files


if sys.platform == "darwin":
    from cx_Freeze.command.bdist_mac import bdist_mac

    class IconComposerBdistMac(bdist_mac):
        def create_plist(self):
            with tempfile.TemporaryDirectory() as temporary_directory:
                partial_plist = os.path.join(temporary_directory, "Info.plist")
                subprocess.run(
                    [
                        "xcrun",
                        "actool",
                        "--compile",
                        self.resources_dir,
                        "--platform",
                        "macosx",
                        "--minimum-deployment-target",
                        "11.0",
                        "--app-icon",
                        MACOS_ICON_NAME,
                        "--output-partial-info-plist",
                        partial_plist,
                        MACOS_ICON_PATH,
                    ],
                    check=True,
                )
                with open(partial_plist, "rb") as stream:
                    icon_plist = plistlib.load(stream)

            self.plist_items.extend(icon_plist.items())
            super().create_plist()


build_exe_options = {
    "packages": PACKAGES,
    "include_files": INCLUDE_FILES + collect_ui_files(),
    "excludes": [
        "PyQt6.QtSql",
        "tkinter",
        "numpy",
        "pydoc_data",
        "distutils",
        "setuptools",
    ],
    "optimize": 2,
}

base = "Win32GUI" if sys.platform == "win32" else None
if sys.platform == "win32":
    build_exe_options["include_msvcr"] = True

executables = [
    Executable(
        "src/main.py",
        base=base,
        icon=ICON_PATH if sys.platform == "win32" else None,
        shortcut_dir="ProgramMenuFolder" if sys.platform == "win32" else None,
        target_name="TeleScore",
    )
]

options = {"build_exe": build_exe_options}
if sys.platform == "darwin":
    options["bdist_mac"] = {
        "bundle_name": "TeleScore",
    }

setup(
    name="TeleScore",
    version="1.0",
    description="TeleScore - Open Source Scoreboard Software",
    options=options,
    executables=executables,
    cmdclass={"bdist_mac": IconComposerBdistMac} if sys.platform == "darwin" else {},
)