Introduction
--------------

This is a task squashing tool, written in Python with pyGTK, that loosely is based on ideas from GTD and Kanban. Developed on Windows but should be relatively cross platform. It accepts tasks from a Zim Desktop Wiki logs your task squashing activity.

Current features:
--------------
* Supports Zim Desktop Formatted tasks with following additions
 * Relative or real effort estimate. Just add the estimate in parenthesis: (4h) or (2p)
* Allows tracking of your task squashing
* Allows tracking of your activity (active window tracking)
* Naive Bayes classifier based learning algorithm nags to you if you do not do the thing you have selected to do.

For now Only the Lite version is available. Run it from command line with
```bash
python taskSquashLite.py
```

Planned features:
--------------
Three views to your task squashing fun:
* A dashboard for defining short term goals (day/week) and planning which tasks are relevant to do next (21p)
 * Lets you to review the incoming tasks by their priority!!! and due dates.
 * Offers semiautomatic planner in form of a gantt chart. It will try to plan when to do the tasks next in line (uses pirority, due date and effort estimate).
* Three pane Kanban influenced layout for Incoming tasks, Active tasks, and Done tasks. This inclides the functionality of the Task Squasher Lite (13p)
* A review pane with reporting (gauges and graphs for task squashing velocity, gantt charts for window and task activity etc.) (34p)


**TODO** (also offers some examples of Zim task format):

[ ] @Implement status to the statusbar to show when task and user activity are being tracked and when the user is teaching the NB classifier. (2h)

[ ] @Write full documentation of the tool (4p)

[ ] @Implement better nagging message. A system modal dialog with random motivational poster would do.. (2h)


