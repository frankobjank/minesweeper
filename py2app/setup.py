from setuptools import setup
from datetime import date

APP =["main.py"]
OPTIONS = {
    'argv_emulation': True,
}

setup(
    name = f"Minesweeper_{date.today()}",
    app = APP,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"]
)