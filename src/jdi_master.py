from pathlib import Path
import subprocess
import os

from jdi_task import jdi_task
from jdi_fs import jdi_fs

class jdi_master:

    MODE_STANDARD = 0
    MODE_DATED = 1
    MODE_TODO = 2
    NUM_MODE = 3
    
    BASEDIR = Path('/home/arleok/repos/justdoit/test/')

    NUM_PANELS = 2

    ### PUBLIC METHODS ###
    def __init__(s):
        s.fs = jdi_fs(Path('/home/arleok/repos/justdoit/test/2/'))
        s.dir = s.BASEDIR / '2/'

        s.mode = s.MODE_STANDARD
        s.showArchived = False

        s.cursor = 0

        s.load()

    def load(s):
        s.paneldata = [[jdi_task("","","","","") for i in range(0)] for k in range(s.NUM_PANELS)]

        if s.mode == s.MODE_STANDARD:
            s.paneldata[0] = s.fs.subtasks(s.dir, 1)
        elif s.mode == s.MODE_DATED:
            s.paneldata[0] = s.fs.subtasks(s.dir, 1)

        s.paneldata[1] = s.fs.subtasks(Path(s.paneldata[0][s.cursor].file).parent, 1)
        s.tasks = [s.fs.taskfromwiki(str(s.dir/'.wiki')), s.paneldata[0][s.cursor]]

    def isCursor(s, task, panel):
        if panel == 1:
            return False
        return task.file == s.paneldata[panel][s.cursor].file

    def cursMV(s, direction):
        s.cursor += direction
        if s.cursor < 0:
            s.cursor = len(s.paneldata[0])-1
        if s.cursor >= len(s.paneldata[0]):
            s.cursor = 0
        s.load()

    def taskMV(s, direction):
        if direction == -1 and s.cursor == 0:
            return
        if direction == 1 and s.cursor == len(s.paneldata[0])-1:
            return
        if s.paneldata[0][s.cursor].date != "":
            return
        if s.paneldata[0][s.cursor+direction].date != "":
            return
        if s.paneldata[0][s.cursor].status ==  'done':
            return
        if s.paneldata[0][s.cursor+direction].status ==  'done':
            return
        
        s.swapFile(str(Path(s.paneldata[0][s.cursor].file).parent), str(Path(s.paneldata[0][s.cursor+direction].file).parent))
        s.cursor += direction
        s.load()

    def swapFile(s, this, that):
        subprocess.run(['mv', this, this+'TEMP'], capture_output=True) 
        subprocess.run(['mv', that, this], capture_output=True) 
        subprocess.run(['mv', this+'TEMP', that], capture_output=True) 

    def changeAttr(s, attr, newval):
        task = s.paneldata[0][s.cursor]
        match attr:
            case 'name':
                oldval = task.name
            case 'date':
                oldval = task.date
            case 'desc':
                oldval = task.desc
            case 'status':
                oldval = task.status
            case 'color':
                oldval = str(task.color)
            case _:
                return

        matchstring = '//jdi-'+attr+'//=='+oldval
        newstring = '//jdi-'+attr+'//=='+newval

        if str(subprocess.run(['grep', matchstring, task.file], capture_output=True).stdout, 'utf-8') == '':
            subprocess.run([str(Path(__file__).parent / 'echointo.sh'), newstring, task.file])
        else:
            subprocess.run(['sed', '-i', 's+'+matchstring+'+'+newstring+'+', task.file])

        s.load()
        if attr == 'date':
            s.alignCursWith(task.name)
            s.load()

    def addTask(s, panel):
        folder = Path(s.tasks[panel].file).parent / (str(subprocess.run(['date', '+%s'], capture_output=True).stdout, 'utf-8').split('\n')[0]+'/')

        foldername = str(folder)
        wikiname = str(folder / '.wiki')
        defaultwikiname = os.path.expandvars('$XDG_CONFIG_HOME/jdi/default.wiki')

        subprocess.run(['mkdir', foldername])
        subprocess.run(['cp', defaultwikiname, wikiname])
        s.load()

    def deleteTask(s):
        folder = str(Path(s.paneldata[0][s.cursor].file).parent)
        subprocess.run(['rm', '-r', folder])
        s.cursor = 0
        s.load()

    def downdir(s):
        if len(s.paneldata[1]) == 0:
            return
        s.dir = Path(s.paneldata[0][s.cursor].file).parent
        s.cursor = 0
        s.load()

    def updir(s):
        if s.dir == s.BASEDIR:
            return
        s.dir = s.dir.parent
        name = s.tasks[0].name

        s.cursor = 0
        s.load()
        s.alignCursWith(name)
        s.load()

    def alignCursWith(s, name):
        for i in range(len(s.paneldata[0])):
            if s.paneldata[0][i].name == name:
                s.cursor = i
                break
