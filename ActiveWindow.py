# -*- coding: utf-8 -*-
"""
Created on Wed Jan 09 16:08:45 2013

@author: juherask
"""

def module_exists(module_name):
    try:
        __import__(module_name)
    except ImportError:
        return False
    else:
        return True
        
def which(program):
    """ Snipplet courtesy of Jay @ Stackoverflow 
    http://stackoverflow.com/a/377028/1788710
    """
    
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def get_active_window_title():
    # For *unixy systems
    if which('xprop'):
        from subprocess import Popen, PIPE
        import re
        
        """ Snipplet courtesy of Alex Spurling @ Stackoverflow
        http://stackoverflow.com/a/4718297/1788710
        """
        
        root = Popen(['xprop', '-root', '_NET_ACTIVE_WINDOW'], stdout=PIPE)
    
        for line in root.stdout:
            m = re.search('^_NET_ACTIVE_WINDOW.* ([\w]+)$', line)
            if m != None:
                id_ = m.group(1)
                id_w = Popen(['xprop', '-id', id_, 'WM_NAME'], stdout=PIPE)
                break
    
        if id_w != None:
            for line in id_w.stdout:
                match = re.match("WM_NAME\(\w+\) = (?P<name>.+)$", line)
                if match != None:
                    return match.group("name")
    
        return None
    # Perhaps we can use win32gui?
    elif module_exists('win32gui'):
        from win32gui import GetWindowText, GetForegroundWindow
        hawnd = GetForegroundWindow()
        return GetWindowText(hawnd) if hawnd else None
    else:
        raise Exception("Sorry, I have no idea how to get the active window title.")
        
def test():
    from time import sleep
    print("Getting the active window after 5 seconds...")
    sleep(5)
    print(get_active_window_title())
    print("Done.")

if __name__=='__main__':
    test()