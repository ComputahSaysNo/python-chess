import sys
import os
from cx_Freeze import setup, Executable

os.environ['TCL_LIBRARY'] = "C:\\Python36\\tcl\\tcl8.6"
os.environ['TK_LIBRARY'] = "C:\\Python36\\tcl\\tk8.6"

base = None

if sys.platform == "win32":
    base = "Win32GUI"

includes = []
include_files = [r"C:\Python36\DLLs\tcl86t.dll",
                 r"C:\Python36\DLLs\tk86t.dll"]

setup(
    name="Chess",
    version="1.0",
    options={"build_exe": {"includes": includes, "include_files": include_files}},
    executables=[Executable(r"C:\Users\kevin\PycharmProjects\python-chess\main.py", base=base)]
)
