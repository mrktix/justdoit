from jdi_task import jdi_task

class jdi_master:

    MODE_STANDARD = 0
    MODE_DATED = 1
    MODE_TODO = 2
    NUM_MODE = 3

    IND_NAME = 0
    IND_DATE = 1
    IND_DESC = 2
    IND_STATUS = 3
    NUM_IND = 4

    MAX_NUM_PANELS = 3

    ### PUBLIC METHODS ###
    def __init__(s):
        s.mode = s.MODE_STANDARD
        s.showArchived = False
        s.load()

    def load(s):
        # paneldata[mode][panel][name, date, desc, status][tasknum]
        maxnumtasks=3
        s.paneldata = [[[[" " for i in range(maxnumtasks)] for j in range(s.NUM_IND)] for k in range(s.MAX_NUM_PANELS)] for l in range(s.NUM_MODE)]
        s.paneldata[s.MODE_STANDARD][0] = [["super one", "super two", "bobby"], ["", "00/00/0000", "01/23/4567"]]
        s.paneldata[s.MODE_STANDARD][1] = [["bobby's child", "bobby has legs"], ["", ""]]
        s.paneldata[s.MODE_STANDARD][2] = [["bobby"], ["16/02/2023"], ["complete all there is to complete about bobby"], ["active"]]

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

    def getCursor(s, mode, panel):
        return 0

    def getColors(s, mode, panel):
        return [0, 0, 8]
