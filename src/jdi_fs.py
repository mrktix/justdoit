from pathlib import Path
import subprocess
import os

from jdi_task import jdi_task
from jdi_parser import jdi_parser

class jdi_fs:

    def __init__(s):
        s.parser = jdi_parser()
        s.showDoneTasks = True

    def toggleShowDoneTasks(s):
        s.showDoneTasks = not s.showDoneTasks
    
    def taskfromwiki(s, wiki):
        return s.parser.parse(wiki)

    def subtasks(s, path, depth):
        return s.sorttasks(s.tasksindir(path, depth))

    def tasksFromFile(s, filestr):
        #stuff
        taskfolders = str(subprocess.run(['cat', filestr], capture_output=True).stdout, 'utf-8').split('\n')[:-1]
        
        tasks=[]
        for folder in taskfolders:
            task = s.taskfromwiki(str(Path(folder) / '.wiki'))
            if task.status ==  'done':
                if s.showDoneTasks:
                    tasks += [task]
            else:
                tasks += [task]

        return tasks

    def tasksindir(s, directory, depth):
        #create list of paths to tasks in this directory
        dirs = [directory]

        for i in range(depth):
            newdirs = []
            for dir in dirs:
                for entry in dir.iterdir():
                    if not os.path.isfile(entry):
                        newdirs += [entry]
            dirs = newdirs

        
        tasks = []
        for dir in dirs:
            tasks += [s.taskfromwiki(str(dir / '.wiki'))]

        return tasks

    def indexOfParent(s, cotasks, subtasks):
        path = str(Path(subtasks[0].file).parent.parent / '.wiki')
        for i in range(len(cotasks)):
            if cotasks[i].file == path:
                return i
        return 0
        
    def sorttasks(s, tasks):
        dated = []
        undated = []
        done = []

        for task in tasks:
            if task.status == 'done':
                if s.showDoneTasks:
                    done += [task]
            elif task.date.find("/") == -1:
                undated += [task]
            else:
                dated += [task]

        #sort dated tasks
        datedsort = [None for i in range(len(dated))]
        for task in dated:
            #loop down sorted
            for i in range(len(datedsort)):
                # if spot is blank, take it
                if datedsort[i] == None:
                    datedsort[i] = task
                    break

                # if this task is earlier, move list over
                if s.firstearly(task.date, datedsort[i].date):
                    # move all of list, up to i, over
                    for j in reversed(range(i, len(datedsort)-1)):
                        datedsort[j+1] = datedsort[j]
                    datedsort[i] = task
                    break

                # this task it later, continue loop
        return datedsort+undated+done

    def firstearly(s, date1, date2):
        sdate1 = date1.split('/')
        sdate2 = date2.split('/')
        if int(sdate1[2]) < int(sdate2[2]):
            return True
        elif int(sdate1[2]) > int(sdate2[2]):
            return False

        if int(sdate1[1]) < int(sdate2[1]):
            return True
        elif int(sdate1[1]) > int(sdate2[1]):
            return False

        if int(sdate1[0]) < int(sdate2[0]):
            return True
        elif int(sdate1[0]) > int(sdate2[0]):
            return False

        return False
