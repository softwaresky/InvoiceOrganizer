import sys
import os
from cx_Freeze import setup, Executable


def make_build(script_target=""):

    # dependencies
    build_exe_options = {
        "packages": ["lib.DbLib"],
        "include_files": [(os.path.abspath("./db/SmetkovotstvenaKniga.db"), "db/SmetkovotstvenaKniga.db"),
                            (os.path.abspath("./stamp/img_stamp.png"), "stamp/img_stamp.png"),
                          (os.path.abspath("./html_template/html_a4_page.html"), "html_template/html_a4_page.html")],
        "excludes": ["Tkinter", "Tkconstants", "tcl", ],
        "includes": ["lib.DbLib"],
        "build_exe": "E:/build_script/SmetkovotstvenaKniga-32"
    }

    executable = [
        Executable(r"{0}".format(script_target),
                   base="Win32GUI",
                   targetName="SmetkovotstvenaKniga.exe")
    ]

    setup(
        name="SmetkovotstvenaKniga",
        version="0.1",
        description="SmetkovotstvenaKniga za Mama!",
        author="Softwaresky",
        options={"build_exe": build_exe_options},
        executables=executable
    )

def main():
    sys.argv.append("build")
    script_target = os.path.abspath("./SmetkovotstvenaKnigaGUI.py")
    make_build(script_target=script_target)

main()