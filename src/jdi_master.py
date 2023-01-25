from pathlib import Path

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

        s.cursor = 1

        s.load()

    def load(s):
        # paneldata[mode][panel][tasknum]
        s.paneldata = [[jdi_task("","","","","") for i in range(0)] for k in range(2)]

        s.paneldata[0] = s.fs.subtasks(s.dir)
        s.paneldata[1] = s.fs.subtasks(Path(s.paneldata[0][s.cursor].file).parent)
#        if len(s.paneldata[0])
        s.tasks = [s.fs.taskfromwiki(str(s.dir/'.wiki'))[0], s.paneldata[0][s.cursor]]

    def cursMV(s, direction):
        s.cursor += direction
        if s.cursor < 0:
            s.cursor = len(s.paneldata[0])-1
        if s.cursor >= len(s.paneldata[0]):
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
        for i in range(len(s.paneldata[0])):
            if s.paneldata[0][i].name == name:
                s.cursor = i
                break
        s.load()

    #def getMaxLen(s, panel, category):
        #res = 0
        #for str in s.paneldata[][panel][category]:
            #if len(str) > res:
                #res = len(str)
        #return res
