from pathlib import Path
import subprocess
import os

from jdi_task import jdi_task
from jdi_fs import jdi_fs

class jdi_master:

    MODE_STANDARD = 0
    MODE_OVERVIEW = 1
    MODE_TODO = 2
    
    BASEDIR = Path('/home/arleok/')

    NUM_PANELS = 2

    def __init__(s, dirstr):
        s.fs = jdi_fs()
        s.BASEDIR = Path(dirstr)
        s.dir = s.BASEDIR
        s.todofile = s.BASEDIR / '.todolist'

        s.newTaskCounter = 0

        s.mode = s.MODE_STANDARD

        s.cursor = 0
        s.overviewDepth = 1

        s.load()

    def load(s):
        s.paneldata = [[jdi_task("","","","","","") for i in range(0)] for k in range(s.NUM_PANELS)]
        s.tasks = [jdi_task("","","","","","") for i in range(2)]

        s.tasks[0] = s.fs.taskfromwiki(str(s.dir/'.wiki'))

        if s.mode == s.MODE_STANDARD:
            s.paneldata[0] = s.fs.subtasks(s.dir, 1)
            s.paneldata[1] = s.fs.subtasks(Path(s.paneldata[0][s.cursor].file).parent, 1)
            s.tasks[1] = s.paneldata[0][s.cursor]

        elif s.mode == s.MODE_OVERVIEW:
            s.paneldata[0] = s.fs.subtasks(s.dir, s.overviewDepth)
            s.paneldata[1] = s.fs.subtasks(s.dir, s.overviewDepth+1)
            s.tasks[1] = s.tasks[0]

        elif s.mode == s.MODE_TODO:
            s.paneldata[0] = s.fs.tasksFromFile(str(s.BASEDIR / '.todolist'))
            if len(s.paneldata[0]) != 0:
                s.paneldata[1] = s.fs.subtasks(Path(s.paneldata[0][s.cursor].file).parent, 1)
                s.tasks[1] = s.paneldata[0][s.cursor]
            else:
                s.paneldata[1] = []
                s.tasks[1] = s.tasks[0]

    def isCursor(s, task, panel):
        if panel == 1:
            return False
        return task.file == s.paneldata[panel][s.cursor].file

    def homeDir(s):
        s.dir = s.BASEDIR
        s.mode = s.MODE_STANDARD
        s.cursor = 0
        s.load()

    def toggleDoneTasks(s):
        s.fs.toggleShowDoneTasks()
        if s.paneldata[0][s.cursor].status == 'done':
            s.mvCursAfterDelTask()
        s.load()

    def isInTodo(s, task):
        return str(subprocess.run(['grep', str(Path(task.file).parent), str(s.todofile)], capture_output=True).stdout, 'utf-8') != ''

    def rmFromTodo(s, task):
        subprocess.run(['sed', '-i', 's|'+str(Path(task.file).parent)+'|DELETE|;/DELETE/d', s.todofile])

    def putInTodo(s, task):
        subprocess.run([str(Path(__file__).parent / 'echointo.sh'), str(Path(task.file).parent), s.todofile])

    def toggleTodo(s):
        if len(s.paneldata[0]) == 0:
            return
        task = s.paneldata[0][s.cursor]
        if s.isInTodo(task):
            s.rmFromTodo(task)
        else:
            if task.status == 'done':
                return
            s.putInTodo(task)
        if s.mode ==  s.MODE_TODO:
            s.mvCursAfterDelTask()
        s.load()

    def setMode(s, modestr):
        if modestr == 'standard':
            s.mode = s.MODE_STANDARD
        elif modestr == 'overview':
            s.mode = s.MODE_OVERVIEW
        elif modestr == 'todo':
            s.mode = s.MODE_TODO

        s.cursor = 0
        s.load()

    def getMode(s):
        if s.mode == s.MODE_STANDARD:
            return 'standard'
        if s.mode == s.MODE_OVERVIEW:
            return 'overview'
        if s.mode == s.MODE_TODO:
            return 'todo'

    def cursMV(s, direction):
        s.cursor += direction
        if s.cursor < 0:
            s.cursor = len(s.paneldata[0])-1
        if s.cursor >= len(s.paneldata[0]):
            s.cursor = 0
        s.load()

    def taskMV(s, direction):
        if s.mode == s.MODE_TODO:
            s.taskMVTD(direction)
            return
        if not s.mode == s.MODE_STANDARD:
            return
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

    def taskMVTD(s, direction):
        if s.mode != s.MODE_TODO:
            return
        if s.cursor + direction < 0:
            return
        if s.cursor + direction >= len(s.paneldata[0]):
            return
        #sed -i -n '20{h;n;G};p' infile (swaps line 20 with the one below)
        if direction == -1:
            targline = s.cursor+direction+1
        else:
            targline = s.cursor+1
        subprocess.run(['sed', '-i', '-n', str(targline)+'{h;n;G};p', str(s.todofile)])
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
                if newval == 'done' and s.isInTodo(task):
                    s.rmFromTodo(task)
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
        if not s.mode == s.MODE_STANDARD:
            return
        folder = Path(s.tasks[panel].file).parent / (str(subprocess.run(['date', '+%s'], capture_output=True).stdout, 'utf-8').split('\n')[0]+str(s.newTaskCounter)+'/')

        s.newTaskCounter = (s.newTaskCounter + 1)%100


        foldername = str(folder)
        wikiname = str(folder / '.wiki')
        defaultwikiname = os.path.expandvars('$XDG_CONFIG_HOME/jdi/default.wiki')

        subprocess.run(['mkdir', foldername])
        subprocess.run(['cp', defaultwikiname, wikiname])
        s.load()

    def goTo(s, factor):
        s.cursor = int(factor * (len(s.paneldata[0]) - 1))
        s.load()

    def mvCursAfterDelTask(s):
        if len(s.paneldata[0]) == 1:
            s.updir()
        else:
            if s.cursor == len(s.paneldata[0])-1:
                s.cursor -= 1

    def deleteTask(s):
        folder = str(Path(s.paneldata[0][s.cursor].file).parent)

        s.mvCursAfterDelTask()

        subprocess.run(['rm', '-r', folder])
        s.load()

    def downdir(s):
        if s.mode == s.MODE_OVERVIEW:
            if len(s.paneldata[0]) == 0:
                return
            s.overviewDepth += 1
            s.cursor = 0
            s.load()
            return
        if len(s.paneldata[1]) == 0:
            return
        s.dir = Path(s.paneldata[0][s.cursor].file).parent
        s.cursor = 0
        if s.mode == s.MODE_TODO:
            s.setMode('standard')
        else:
            s.load()

    def updir(s):
        if s.mode == s.MODE_TODO:
            return
        if s.mode == s.MODE_OVERVIEW:
            if s.overviewDepth == 1:
                return
            s.overviewDepth -= 1
            s.cursor = 0
            s.load()
            return
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
