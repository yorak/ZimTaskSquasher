Zim Task Squasher (Lite)
========================

Introduction
--------------

This is a task squashing tool, written in Python with pyGTK, that is loosely based on ideas from GTD and Kanban. It has been developed on Windows but should be relatively cross platform. It reads tasks from a Zim Desktop Wiki format files, lets you select one to squash, and logs your task squashing activity to a flat text file.

Current features:
--------------
* Reads a Zim Desktop Formatted text file and parses it for task items
* Supports Zim Desktop Formatted tasks with following additions
 * Relative or real effort estimate. Just add the estimate in parenthesis: (4h) or (2p)
 * Optionally: @Enforce that first word is a verb and a tag. 
* Tracks your task squashing
* Optionally tracks your activity (active window tracking)
* Naive Bayes classifier based teachable algorithm nags to you if you do not do the thing you have selected to do.
 * Teach it to connect tags with active window (title)
 * Nag by showing motivational image to you if you stray

For now Only the Lite version is available. It just offers the task squashing and prorastination nagging. Run it from command line with
```bash
> python taskSquashLite.py
```

**TODO** (also offers some examples of Zim task format):
[*] @Implement status to the statusbar to show when task and user activity are being tracked and when the user is teaching the NB classifier. (2h)
[*] @Implement better nagging message. A system modal dialog with random motivational poster would do.. (2h)
[ ] @Write user documentation for the Lite version of the tool (4h)

Planned features:
--------------
Full version will offer three views to your task squashing fun:
* A dashboard for defining short term goals (day/week) and planning which tasks are relevant to do next (21p)
 * Lets you to review the incoming tasks by their priority!!! and due dates.
 * Offers semiautomatic planner in form of a gantt chart. It will try to plan when to do the tasks next in line (uses priority, task precedence, due date and effort estimate to do this).
* A Kanban influenced layout for Incoming (actionable) tasks, Active tasks, and Done tasks (number of columns is user actionable). This pane also includes the functionality of the Task Squasher Lite (13p)
* A review pane with reporting (gauges and graphs for task squashing velocity, gantt charts for window and task activity etc.) (34p)



