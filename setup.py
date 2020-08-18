import sys
import os
from cx_Freeze import setup, Executable


def make_build(script_target=""):

    # dependencies
    build_exe_options = {
        "packages": ["lib.DbLib"],
        "include_files": [(os.path.abspath("./db/InvoiceOrganizer.db"), "db/InvoiceOrganizer.db"),
                            (os.path.abspath("./stamp/img_stamp.png"), "stamp/img_stamp.png"),
                          (os.path.abspath("./html_template/html_a4_page.html"), "html_template/html_a4_page.html")],
        "excludes": ["Tkinter", "Tkconstants", "tcl", ],
        "includes": ["lib.DbLib"],
        "build_exe": "./build_script/InvoiceOrganizer-x64-win"
    }

    executable = [
        Executable(r"{0}".format(script_target),
                   base="Win32GUI",
                   targetName="InvoiceOrganizer.exe")
    ]

    setup(
        name="InvoiceOrganizer",
        version="0.1",
        description="InvoiceOrganizer for import / export invoices!",
        author="Softwaresky",
        options={"build_exe": build_exe_options},
        executables=executable
    )

def main():
    sys.argv.append("build")
    script_target = os.path.abspath("./InvoiceOrganizerGUI.py")
    make_build(script_target=script_target)

main()