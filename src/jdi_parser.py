import subprocess
from jdi_task import jdi_task

class jdi_parser:

    def __init__(s):
        pass

    def parse(s, parser, path):
        name = str(subprocess.run([parser, 'name', path], capture_output=True).stdout, 'utf-8').split('\n')[:-1]
        date = str(subprocess.run([parser, 'date', path], capture_output=True).stdout, 'utf-8').split('\n')[:-1]
        desc = str(subprocess.run([parser, 'desc', path], capture_output=True).stdout, 'utf-8').split('\n')[:-1]
        status = str(subprocess.run([parser, 'status', path], capture_output=True).stdout, 'utf-8').split('\n')[:-1]

        numtasks = max(len(name), len(date), len(desc), len(status))
        name += ["" for i in range(numtasks-len(name))]
        date += ["" for i in range(numtasks-len(date))]
        desc += ["" for i in range(numtasks-len(desc))]
        status += ["" for i in range(numtasks-len(status))]

        tasks = [jdi_task("","","","","") for i in range(numtasks)]

        for i in range(numtasks):
            tasks[i].name = name[i]
            tasks[i].date = date[i]
            tasks[i].desc = desc[i]
            tasks[i].status = status[i]
            tasks[i].file = path

        return tasks


parser = jdi_parser()
parser.parse('/home/arleok/repos/justdoit/src/wikiparser.sh', '/home/arleok/repos/justdoit/test/.wiki')
