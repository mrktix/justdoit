import curses
from curses import wrapper
from curses.textpad import rectangle

from jdi_master import jdi_master
from jdi_task import jdi_task
from jdi_config import jdi_config

def taskPanel(h, w, x0, x1, y0, y1, panel, master, sth):
    padw = x1-x0-2
    pad = curses.newpad(len(master.paneldata[panel])+1, padw+1)

    i = 0
    for task in master.paneldata[panel]:
        attr = curses.A_NORMAL
        if master.cursor == i and panel == 0:
            attr = curses.A_REVERSE

        pad.addstr(i, 0, " "*padw, attr)
        pad.addstr(i, 0, task.name[:padw], attr)
        if padw-len(task.name) >= len(task.date)+1:
            pad.addstr(i, padw-len(task.date), task.date, attr)

        i += 1

    pad.refresh(0, 0, y0+1, x0+1, y1-1, x1-2) 
    #sth.addstr(y0, x0+1, master.tasks[panel].name[:padw])

def descPanel(h, w, x0, x1, y0, y1, panel, master, sth):
    padw = x1-x0-2
    padh = y1-y0-2

    task = master.tasks[panel]

    desclines = ["" for i in range(len(task.desc)//padw+1)]
    for i in range(len(desclines)):
        desclines[i] = task.desc[i*padw:(i+1)*padw]

    descpad = curses.newpad(len(desclines)+1, padw+1)
    i = 0
    for line in desclines:
        descpad.addstr(i, 0, line)
        i += 1

    descpad.refresh(0, 0, y0+1, x0+1, y1-1, x1-2)

    #sth.addstr(y0, x0+1, task.name[:padw])
    sth.addstr(y0+padh+2, x0+1, task.date[:padw])
    if padw-len(task.date)-1 >= len(task.status):
        sth.addstr(y0+padh+2, x0+padw+1-len(task.status), task.status)

def taskRect(x0, x1, y0, y1, panel, master, sth):
    rectangle(sth, y0, x0, y1-1, x1-1)
    sth.addstr(y0, x0+1, master.tasks[panel].name[:x1-x0-2])

def main(sth):
    curses.curs_set(0)
    curses.use_default_colors()
    #in initpair, -1 will give default (in this case transparent bg)
    master = jdi_master()
    fig = jdi_config()
    binds = fig.load()
    mode = 'normal'
    mode2 = ''
    buffer = ''

    while True:
        h, w = sth.getmaxyx()
        pw = (w-2)/(master.NUM_PANELS+1)
        p0x, p1x, p2x, p3x = int(0*pw)+1, int(1*pw)+1, int(2*pw)+1, int(3*pw)+1

        ph = (h-1)/(2)
        p0y, p1y, p2y = int(0*ph), int(1*ph), int(2*ph)
        #y0, y1 = 0, h-1

        sth.clear()###
        taskRect(p0x, p1x, p0y, p2y, 0, master, sth)
        taskRect(p1x, p2x, p0y, p2y, 1, master, sth)

        taskRect(p2x, p3x, p0y, p1y, 0, master, sth)
        taskRect(p2x, p3x, p1y, p2y, 1, master, sth)
        sth.refresh()###

        taskPanel(h, w, p0x, p1x, p0y, p2y-1, 0, master, sth)
        taskPanel(h, w, p1x, p2x, p0y, p2y-1, 1, master, sth)
        descPanel(h, w, p2x, p3x, p0y, p1y-1, 0, master, sth)
        descPanel(h, w, p2x, p3x, p1y, p2y-1, 1, master, sth)

        if mode2 == '':
            modestr='['+mode+']'
        else:
            modestr='['+mode+' '+mode2+']'

        sth.addstr(h-1, 1, modestr[:w-2])
        spaceforbuffer = w-2-len(modestr)-1
        sth.addstr(h-1, len(modestr)+2, buffer[-spaceforbuffer:])
        
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
            elif buffer == binds['up']:
                master.cursMV(-1)
            elif buffer == binds['down']:
                master.cursMV(1)
            elif buffer == binds['right']:
                master.downdir()

            elif buffer == binds['mvup']:
                master.taskMV(-1)
            elif buffer == binds['mvdn']:
                master.taskMV(1)

            elif buffer == binds['chname']:
                mode = 'change'
                mode2 = 'name'
            elif buffer == binds['chdate']:
                mode = 'change'
                mode2 = 'date'
            elif buffer == binds['chdesc']:
                mode = 'change'
                mode2 = 'desc'
            elif buffer == binds['chstatus']:
                mode = 'change'
                mode2 = 'status'

            elif buffer == binds['quit']:
                break
            else:
                clr = False
        elif mode == 'change' and not skip:
            if key == '\n':
                master.changeAttr(mode2, buffer)
                mode = 'normal'
                mode2 = ''
            else:
                clr = False

        if clr:
            buffer = ''

wrapper(main)
