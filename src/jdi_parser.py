import subprocess
from jdi_task import jdi_task
from pathlib import Path

class jdi_parser:

    def __init__(s):
        s.parser = Path(__file__).parent / 'wikiparser.sh'

    def parse(s, path):
        name = str(subprocess.run([s.parser, 'name', path], capture_output=True).stdout, 'utf-8').split('\n')[0]
        date = str(subprocess.run([s.parser, 'date', path], capture_output=True).stdout, 'utf-8').split('\n')[0]
        desc = str(subprocess.run([s.parser, 'desc', path], capture_output=True).stdout, 'utf-8').split('\n')[0]
        status = str(subprocess.run([s.parser, 'status', path], capture_output=True).stdout, 'utf-8').split('\n')[0]
        colorstr = str(subprocess.run([s.parser, 'color', path], capture_output=True).stdout, 'utf-8').split('\n')[0]
        if colorstr == '':
            color = 7
        else:
            color = int(colorstr)

        return jdi_task(name, date, desc, status, color, path)
