import subprocess
import os
from pathlib import Path

class jdi_config:
    def __init__(s):
        s.configfile = os.path.expandvars('$XDG_CONFIG_HOME/jdi/config')
        s.binds = {}

    def load(s):
        config = str(subprocess.run(['cat', s.configfile], capture_output=True).stdout, 'utf-8').split('\n')[:-1]
        for line in config:
            args = line.split(' ')
            if len(args) < 2:
                continue
            s.binds[args[0]] = args[1]
        return s.binds

        
