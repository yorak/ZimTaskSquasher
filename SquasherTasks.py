# -*- coding: utf-8 -*-
"""
Created on Tue Jan 08 14:53:03 2013

@author: juherask
"""

import re
from dateutil import parser

from ReplaceInFile import replace

""" The main task data structure (as namedtuple) """
class Task:
    def __init__(self,
        taskline,
        state,
        verb,
        task,
        tags,
        details,
        due,
        priority,
        effortEstimate,
        effortReal):
    
        self.taskline = taskline
        self.state = state
        self.verb = verb
        self.task = task
        self.tags = tags
        self.details = details
        self.due = due
        self.priority = priority
        self.effortEstimate = effortEstimate
        self.effortReal = effortReal
 
## Some regular expressions that are used in task parsing ## 
headerRe = re.compile("=====\s+.*?\s+=====")
taskRe = re.compile(r"""
    ^\s*            # Whitespace at the start of the line
    \[([*Xx ])\]    # The check mark that defines this line being a task
                    #  group(1) being the state of the check mark
    \s+([@\w]+)\s+  # First one of the task that is typically a verb (can be a @tag)
    ([^.!\(]+)     # Rest of the sentence describing the task
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


def save_task_state_change(toFileName, task):
    fromstr = task.taskline    
    tostr = re.sub(r'^(\s*)\[([*Xx ])\]', r'\1[%s]'%task.state, task.taskline)
    
    # Use helper function for repace the line in the source file
    replace(toFileName, fromstr, tostr)
    
def load_task_list(fromFileName, withSettings):
        
    taskfile = open(fromFileName, 'r')
    readtarget = None
    detailstarget = None
    headersAvailable = withSettings['tasks_organized_under_headers']
    
    tasksIn = []
    tasksDo = []
    tasksOut = []
    tasksRej = []
    
    if not headersAvailable:
        readtarget = tasksIn 
    
    while 1:
        line = taskfile.readline()
        if not line:
            break

        if headersAvailable and headerRe.search(line):
            readtarget = None
            detailstarget = None
            
            if withSettings['text_in_header'] in line:
                readtarget = tasksIn
            elif withSettings['text_do_header'] in line:
                readtarget = tasksDo
            elif withSettings['text_out_header'] in line:
                readtarget = tasksOut
            elif withSettings['text_rejected_header'] in line:
                readtarget = tasksRej
            
            continue
        
        # Check if the line contains a task  
        newTask = line_to_task(line)
        if newTask and readtarget!=None:
            # If the tasks are not organized under headers, use the state 
            #  to determine the bin for the task.
            if not headersAvailable:
                if newTask.state==' ':
                    readtarget = tasksIn
                elif newTask.state=='*':
                    readtarget = tasksOut
                elif newTask.state=='X':
                    readtarget = tasksRej
            
            readtarget.append(newTask)
            # Collect following lines detailing the task here
            detailstarget = newTask.details                
        
        # If there is active task details object. Pass all the following
        #  lines to its details field.
        elif readtarget!=None and detailstarget!=None:
            detailstarget.append(line)
    
    
    return tasksIn, tasksDo, tasksOut, tasksRej