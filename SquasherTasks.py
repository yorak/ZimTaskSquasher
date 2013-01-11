# -*- coding: utf-8 -*-
"""
Created on Tue Jan 08 14:53:03 2013

@author: juherask
"""

import re
from collections import namedtuple
from dateutil import parser

""" The main task data structure (as namedtuple) """
Task = namedtuple('Task', ['taskline', 'state', 'verb', 'task', 'tags', 'details',
                           'due', 'priority', 'effortEstimate', 'effortReal'])
 
## Some regular expressions that are used in task parsing ## 
headerRe = re.compile("=====\s+.*?\s+=====")
taskRe = re.compile(r"""
    ^\s*            # Whitespace at the start of the line
    \[([*Xx ])\]    # The check mark that defines this line being a task
                    #  group(1) being the state of the check mark
    \s+([@\w]+)\s+  # First one of the task that is typically a verb (can be a @tag)
    ([^.!]+)        # Rest of the sentence describing the task
    .*?             # All the rest
    """, re.VERBOSE)
tagRe = re.compile("\s+(@[\w]+)[\s!?.,]+")
dueRe = re.compile("\[d:\s([\d\-/]+)\]")     
# priority as concecutive Exclamation marks
priorityRe = re.compile("!+");
# effort estinate of the form (11.5/12h) where the first part is optional
effortRe = re.compile("\(((\d+\.?\d*)/)?(\d+)[hp]\)") 


def line_to_task(line):
    # Check if line contains a task
    taskMatch = taskRe.search(line)
    if taskMatch:
        # Try to get the optional priority                
        taskPriority = 0
        priorityMatches = priorityRe.findall(line)
        if len(priorityMatches)>0:                    
            # Longest group of ! characters determines priority (number of !)
            taskPriority = len(max(priorityMatches))
            
        # Try to get optional due date field                
        parsedDue = None
        dueMatch = dueRe.search(line)
        if dueMatch:
            parsedDue = parser.parse(dueMatch.group(1))
        
        # Optional effort field
        taskEffortReal = None
        taskEffortEstimate = None
        effortMatch = effortRe.search(line)
        if effortMatch:
            if effortMatch.group(2):
                taskEffortReal=float(effortMatch.group(2))
            if effortMatch.group(3):
                taskEffortEstimate=int(effortMatch.group(3))

        newTask = Task(
            taskline = line.rstrip('\n'),
            state = taskMatch.group(1).upper(), 
            verb = taskMatch.group(2),
            task = taskMatch.group(3).rstrip('\n'),
            tags = tagRe.findall(line),
            details = [],
            due = parsedDue, priority = taskPriority,
            effortEstimate=taskEffortEstimate, effortReal=taskEffortReal)
        
        return newTask
    else:
        return None