import curses
import math
import subprocess
from curses import wrapper
from curses.textpad import rectangle

from jdi_master import jdi_master
from jdi_task import jdi_task
from jdi_config import jdi_config

def initCols():
    termcolors = [curses.COLOR_BLACK, curses.COLOR_RED, curses.COLOR_GREEN, curses.COLOR_YELLOW, curses.COLOR_BLUE, curses.COLOR_MAGENTA, curses.COLOR_CYAN, -1]

    for i in range(len(termcolors)):
        curses.init_pair(i+1, termcolors[i], -1)

def taskColor(task, panel, master, highlightCurs):
    color = curses.color_pair(task.color+1)

    if task.status ==  'done':
        color = curses.color_pair(1) | curses.A_BOLD
    if highlightCurs and master.isCursor(task, panel):
        color = color | curses.A_REVERSE | curses.A_BOLD

    return color

def taskPanel(h, w, x0, x1, y0, y1, scroll, panel, master, sth):
    padw = x1-x0-2
    pad = curses.newpad(len(master.paneldata[panel])+1, padw+1)

    i = scroll
    for height in range(len(master.paneldata[panel])-scroll):
        task = master.paneldata[panel][i]
        color = taskColor(task, panel, master, True)

        pad.addstr(height, 0, " "*padw, color)
        pad.addstr(height, 0, task.name[:padw], color)
        datestr = dateString(task.date)
        if padw-len(task.name) >= len(datestr)+1:
            pad.addstr(height, padw-len(datestr), datestr, color)

        i += 1

    pad.refresh(0, 0, y0+1, x0+1, y1-1, x1-2) 

def descPanel(h, w, x0, x1, y0, y1, panel, master, sth):
    padw = x1-x0-2
    padh = y1-y0-2

    task = master.tasks[panel]
    color = taskColor(task, panel, master, False)

    desclines = ["" for i in range(len(task.desc)//padw+1)]
    for i in range(len(desclines)):
        desclines[i] = task.desc[i*padw:(i+1)*padw]

    descpad = curses.newpad(len(desclines)+1, padw+1)
    i = 0
    for line in desclines:
        descpad.addstr(i, 0, line, color)
        i += 1

    descpad.refresh(0, 0, y0+1, x0+1, y1-1, x1-2)

def getDescHeight(w, panel, master):
    return math.ceil(len(master.tasks[panel].desc)//w)

def infoRect(x0, x1, y0, y1, panel, master, sth, info):
    task = master.tasks[panel]
    sth.attron(taskColor(task, panel, master, False))

    rectangle(sth, y0, x0, y1-1, x1-1)

    if info:
        sth.addstr(y0, x0+1, task.name[:x1-x0-2])
        sth.addstr(y1-1, x0+1, task.date[:x1-x0-2])
        if x1-x0-2-len(task.date) > len(task.status):
            sth.addstr(y1-1, x1-len(task.status)-1, task.status)

    sth.attroff(taskColor(task, panel, master, False))

def dateString(date):
    if date ==  '':
        return ''
    dateBAD = date[3:6]+date[:3]+date[-4:]
    return str(subprocess.run(['date', '-d', dateBAD, '+%A %b %d %y'], capture_output=True).stdout, 'utf-8').split('\n')[0]

def dateAutoFill(date):
    if date == 'today':
        return str(subprocess.run(['date', '+%d/%m/%Y'], capture_output=True).stdout, 'utf-8').split('\n')[0]

    datesplit = date.split('/')
    newdate = ''
    for num in datesplit:
        if len(num) == 1:
            newdate += '0' + num + '/'
        else:
            newdate += num + '/'
    newdate = newdate[:-1]

    numslash = newdate.count('/')
    if numslash ==  0:
        #assume input is the day
        return newdate + str(subprocess.run(['date', '+/%m/%Y'], capture_output=True).stdout, 'utf-8').split('\n')[0]
    elif numslash ==  1:
        #assume input is the day and month
        return newdate + str(subprocess.run(['date', '+/%Y'], capture_output=True).stdout, 'utf-8').split('\n')[0]

def main(sth):
    curses.curs_set(0)
    curses.use_default_colors()
    initCols()

    master = jdi_master()
    fig = jdi_config()
    binds = fig.load()
    mode = 'normal'
    mode2 = ''
    buffer = ''

    scroll = 0

    while True:
        #pw = int((w-2)*0.5)
        #p0x, p1x, p2x = int(0*pw)+1, int(1*pw)+1, int(2*pw)+1
        #ph = int((h-1)*0.7)
        #p0y, p1y, p2y = 0, 0+ph, h-1
        h, w = sth.getmaxyx()

        p0x = 1
        p1x = w//2
        p2x = w-1

        leftDescHeight = getDescHeight(p1x-p0x-4, 0, master)
        rightDescHeight = getDescHeight(p2x-p1x-4, 1, master)

        p0y = 0
        p1yl = h-4-leftDescHeight
        p1yr = h-4-rightDescHeight
        p2y = h-1

        sth.clear()###
        infoRect(p0x, p1x, p0y, p2y, 0, master, sth, True)
        infoRect(p1x, p2x, p0y, p2y, 1, master, sth, True)
        sth.refresh()###

        taskPanel(h, w, p0x, p1x, p0y, p1yl-1, scroll, 0, master, sth)
        taskPanel(h, w, p1x, p2x, p0y, p1yr-1, 0, 1, master, sth)
        descPanel(h, w, p0x+1, p1x-1, p1yl-1, p2y-1, 0, master, sth)
        descPanel(h, w, p1x+1, p2x-1, p1yr-1, p2y-1, 1, master, sth)

        modecolor = curses.color_pair(8)
        match mode:
            case 'change':
                modecolor = curses.color_pair(3)
            case 'set':
                modecolor = curses.color_pair(5)
            case 'delete':
                modecolor = curses.color_pair(2)

        if mode2 == '':
            modestr='['+mode+']'
        else:
            modestr='['+mode+' '+mode2+']'

        sth.attron(modecolor)

        sth.addstr(h-1, 1, modestr[:w-2])
        spaceforbuffer = w-2-len(modestr)-1
        sth.addstr(h-1, len(modestr)+2, buffer[-spaceforbuffer:])

        sth.attroff(modecolor)
        
        key = sth.getkey()

        skip = True
        match key:
            case 'KEY_BACKSPACE':
                buffer = buffer[:-1]
            case '\t':
                mode = 'normal'
                mode2 = ''
                buffer = ''
            case _:
                if key.find('KEY') == -1:
                    if key != '\n':
                        buffer += key
                    skip = False

        clr = not skip
        if mode == 'normal' and not skip:
            if buffer == binds['left']:
                master.updir()
                scroll = 0
            elif buffer == binds['up']:
                master.cursMV(-1)
            elif buffer == binds['down']:
                master.cursMV(1)
            elif buffer == binds['right']:
                master.downdir()
                scroll = 0

            elif buffer == binds['mvup']:
                master.taskMV(-1)
            elif buffer == binds['mvdn']:
                master.taskMV(1)

            elif buffer == binds['scrlup']:
                if scroll > 0:
                    master.cursMV(-1)
                    scroll -= 1
            elif buffer == binds['scrldn']:
                if len(master.paneldata[0]) - scroll > p1yl - p0y - 2:
                    master.cursMV(1)
                    scroll += 1

            elif buffer == binds['chname']:
                mode = 'change'
                mode2 = 'name'
            elif buffer == binds['chdate']:
                mode = 'change'
                mode2 = 'date'
            elif buffer == binds['chdesc']:
                mode = 'change'
                mode2 = 'desc'

            elif buffer == binds['setstatus']:
                mode = 'set'
                mode2 = 'status'
            elif buffer == binds['setcolor']:
                mode = 'set'
                mode2 = 'color'

            elif buffer == binds['addtask']:
                master.addTask(0)
            elif buffer == binds['addsubtask']:
                master.addTask(1)

            elif buffer == binds['deletetask']:
                mode = 'delete'
                mode2 = 'task?'

            elif buffer == binds['quit']:
                break
            else:
                clr = False

        elif mode == 'change' and not skip:
            if key == '\n':
                if mode2 ==  'date':
                    buffer = dateAutoFill(buffer)
                master.changeAttr(mode2, buffer)
                mode = 'normal'
                mode2 = ''
            else:
                clr = False

        elif mode == 'delete' and mode2 == 'task?' and not skip:
            if key == '\n':
                if buffer == 'YES':
                    master.deleteTask()
                mode = 'normal'
                mode2 = ''
            else:
                clr = False

        elif mode == 'set' and not skip:
            if mode2 == 'color' and 48 <= ord(buffer) and ord(buffer) <= 55:
                master.changeAttr(mode2, buffer)
            elif mode2 == 'status':
                if buffer == 'd':
                    master.changeAttr(mode2, 'done')
                elif buffer == 'a':
                    master.changeAttr(mode2, 'archived')
                elif buffer == 'A':
                    master.changeAttr(mode2, 'active')

            mode = 'normal'
            mode2 = ''

        if clr:
            buffer = ''

wrapper(main)
