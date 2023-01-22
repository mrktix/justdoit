from pathlib import Path

from jdi_task import jdi_task
from jdi_fs import jdi_fs

class jdi_master:

    MODE_STANDARD = 0
    MODE_DATED = 1
    MODE_TODO = 2
    NUM_MODE = 3

    MAX_NUM_PANELS = 2

    ### PUBLIC METHODS ###
    def __init__(s):
        s.fs = jdi_fs(Path('/home/arleok/repos/justdoit/test/2/'))

        s.mode = s.MODE_STANDARD
        s.showArchived = False

        s.cursor = 0

        s.load()

    def load(s):
        # paneldata[mode][panel][tasknum]
        s.paneldata = [[[jdi_task("","","","","") for i in range(0)] for k in range(s.MAX_NUM_PANELS)] for l in range(s.NUM_MODE)]

        s.paneldata[s.MODE_STANDARD][1] = s.fs.cotasks()
        s.paneldata[s.MODE_STANDARD][0] = s.fs.subtasks()

        print(str(len(s.paneldata[s.MODE_STANDARD][0])))

    def cursMV(direction):
        s.cursor += direction
        if s.cursor < 0:
            s.cursor = s.panel

    def getMode(s):
        return s.mode

    def getNumPanels(s):
        return len(s.paneldata[s.mode])

    def getPanelData(s):
        return s.paneldata[s.mode]

    def getMaxLen(s, panel, category):
        res = 0
        for str in s.paneldata[s.mode][panel][category]:
            if len(str) > res:
                res = len(str)
        return res

    def getCursor(s, panel):
        if panel == 1:
            return s.fs.indexOfParent(s.paneldata[s.mode][0], s.paneldata[s.mode][1])
        else:
            return s.cursor

    def getColors(s, mode, panel):
        return [0, 0, 8]
