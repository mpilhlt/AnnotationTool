import sys

from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
additional_modules = []

build_exe_options = {"includes": additional_modules,
                     "packages": ["pygame", "random", "sys", "pyglet"],
                     #"excludes": ['tkinter'],
                     #"include_files": ['icon.ico', 'res']
                     }

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name="AnnotationTool",
      version="0.2",
      description="Annotate TEI XML files",
      options={"build_exe": build_exe_options},
      executables=[Executable(script="AnnotationToolGUI.py", base=base)])