import curses
from curses import wrapper
from curses.textpad import rectangle

from jdi_master import jdi_master

def taskPanel(h, w, x0, x1, y0, y1, panel, master, sth):
    padw = x1-x0-2
    namepad = curses.newpad(len(master.getPanelData()[panel][master.IND_NAME])+1, padw+1)

    i = 0
    for name in master.getPanelData()[panel][master.IND_NAME]:
        namepad.addstr(i, 0, name[:padw])

        spaceleft = padw-len(name)
        date = master.getPanelData()[panel][master.IND_DATE][i]
            
        if spaceleft >= len(date)+1:
            namepad.addstr(i, padw-len(date), date)
            bob = 1

        i += 1

    namepad.refresh(0, 0, y0+1, x0+1, y1-1, x1-2) 

def main(sth):
    master = jdi_master()

    while True:
        h, w = sth.getmaxyx()
        pw = (w-2)/master.getNumPanels()
        p0x, p1x, p2x, p3x = int(0*pw)+1, int(1*pw)+1, int(2*pw)+1, int(3*pw)+1
        y0, y1 = 0, h-1

        sth.clear()
        rectangle(sth, y0, p0x, y1, p1x-1)
        rectangle(sth, y0, p1x, y1, p2x-1)
        rectangle(sth, y0, p2x, y1, p3x-1)
        sth.refresh()

        taskPanel(h, w, p0x, p1x, y0, y1, 0, master, sth)
        taskPanel(h, w, p1x, p2x, y0, y1, 1, master, sth)

        if sth.getkey() == 'q':
            break


wrapper(main)
