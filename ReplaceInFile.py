# -*- coding: utf-8 -*-
"""
author: Thomas Watnedal 
source: http://stackoverflow.com/a/39110/1788710
"""

from tempfile import mkstemp
from shutil import move
from os import remove, close

def replace(file, pattern, subst):    
    #Create temp file
    fh, abs_path = mkstemp()
    new_file = open(abs_path,'w')
    old_file = open(file)
    for line in old_file:
        new_file.write(line.replace(pattern, subst))
    #close temp file
    new_file.close()
    close(fh)
    old_file.close()
    #Remove original file
    remove(file)
    #Move new file
    move(abs_path, file)