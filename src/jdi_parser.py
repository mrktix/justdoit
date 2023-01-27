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
        #color = str(subprocess.run([s.parser, 'color', path], capture_output=True).stdout, 'utf-8').split('\n')[0]

        return jdi_task(name, date, desc, status, path)

        #numtasks = max(len(name), len(date), len(desc), len(status))
        #name += ["" for i in range(numtasks-len(name))]
        #date += ["" for i in range(numtasks-len(date))]
        #desc += ["" for i in range(numtasks-len(desc))]
        #status += ["" for i in range(numtasks-len(status))]
#
        #tasks = [jdi_task("","","","","") for i in range(numtasks)]
#
        #for i in range(numtasks):
            #tasks[i].name = name[i]
            #tasks[i].date = date[i]
            #tasks[i].desc = desc[i]
            #tasks[i].status = status[i]
            #tasks[i].file = path
#
        #return tasks
