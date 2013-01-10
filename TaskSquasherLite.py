# -*- coding: utf-8 -*-
"""
Created on Tue Jan 08 14:10:00 2013

@author: juherask
"""


#!/usr/bin/env python

import sys
try:
    import pygtk
    pygtk.require("2.0")
except:
  	pass
try:
    import gtk
    import gtk.glade
    import gobject
except:
	sys.exit(1)
 
import SquasherConfig
import SquasherTasks
import datetime

from ActiveWindow import get_active_window_title
from WindowsIdle import get_idle_time

## Data structures etc. ##

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)
States = enum('WAIT_NEW', 'STARTED', 'POSTPONED', 'STOPPED', 'DONE')  
        
class TaskSquasherLiteWindow:
    
    
    ## Member variables ##
    
    settings = SquasherConfig.defaultSettings
    task_activity_log_file = None
    user_activity_log_file = None
   
    workaround_block_signals = False
    state = States.WAIT_NEW
    activeTask = None
    lastActiveWindowTitle = None
    userIdle = False
    
    ## Helper methods ##
    
    @staticmethod
    def log_activity(logfile, task, activity):
        if logfile:
            dtstamp = datetime.datetime.now()
            act = "%s\t%s\t%s\n" % (dtstamp.isoformat(), activity.upper(), task) 
            logfile.write(act)

    ## Signal callback functions. ##
    
    def on_toolbuttonLater_clicked(self, widget, data=None):
        # Stop active task
        if self.activeTask and self.state == States.STARTED:
            taskText = self.activeTask.verb+" "+self.activeTask.task
            self.log_activity(self.task_activity_log_file, taskText, "STOPPED")
            self.log_activity(self.task_activity_log_file, taskText, "POSTPONED")
            
        self.state = States.WAIT_NEW
        self.activeTask = None
        self.workaround_block_signals = True
        self.entryTaskWidget.set_sensitive(True)
        self.doWidget.set_active(False)
        self.pauseWidget.set_active(False)
        self.workaround_block_signals = False
        
        # clears it
        self.entryTaskWidget.set_text("")
        
    def on_toolbuttonDo_clicked(self, widget, data=None):
        if self.workaround_block_signals:
            return
        if self.state == States.STARTED:
            self.workaround_block_signals = True
            widget.set_active(True)
            self.workaround_block_signals = False
            return
        
        
        taskLine = self.entryTaskWidget.get_text()        
        task = SquasherTasks.line_to_task(taskLine)
        
        if self.settings['require_zim_task_format'] and not task:
            md = gtk.MessageDialog(self.window, 
                gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, 
                gtk.BUTTONS_CLOSE, "Task is not of Zim format")
            md.run()
            md.destroy()
            
            self.workaround_block_signals = True
            self.doWidget.set_active(False)
            self.pauseWidget.set_active(False)
            self.workaround_block_signals = False

        else:            
            self.activeTask = task
            taskText = self.activeTask.verb+" "+self.activeTask.task
            self.state = States.STARTED
            self.log_activity(self.task_activity_log_file, taskText, "STARTED")
            
            self.workaround_block_signals = True
            self.entryTaskWidget.set_sensitive(False)
            self.doWidget.set_active(True)
            self.pauseWidget.set_active(False)
            self.workaround_block_signals = False
        
    def on_toolbuttonPause_clicked(self, widget, data=None):
        if self.workaround_block_signals:
            return
            
        if not self.activeTask:
            self.workaround_block_signals = True
            widget.set_active(False)
            self.workaround_block_signals = False
            return
        
        taskText = self.activeTask.verb+" "+self.activeTask.task
        
        if  self.state == States.STARTED:
            self.workaround_block_signals = True
            self.pauseWidget.set_active(True)
            self.workaround_block_signals = False
            self.state = States.STOPPED
            self.log_activity(self.task_activity_log_file, taskText, "STOPPED")
        # From paused state to started
        elif  self.state == States.STOPPED:
            self.workaround_block_signals = True
            self.pauseWidget.set_active(False)
            self.workaround_block_signals = False
            self.state = States.STARTED
            self.log_activity(self.task_activity_log_file, taskText, "STARTED")
        # Prevent press if pausing makes no sense
        else:
            self.workaround_block_signals = True
            self.pauseWidget.set_active(False)
            self.workaround_block_signals = False
        
            
    def on_toolbuttonDone_clicked(self, widget, data=None):
        if not self.activeTask:
            return
            
        taskText = self.activeTask.verb+" "+self.activeTask.task
        
        if  self.state == States.STARTED or self.state == States.STOPPED:
            self.workaround_block_signals = True
            self.pauseWidget.set_active(False)
            self.doWidget.set_active(False)
            self.entryTaskWidget.set_sensitive(True)
            self.workaround_block_signals = False

            # For easier parsing, go to DONE trough STOPPED
            self.log_activity(self.task_activity_log_file, taskText, "STOPPED")            
            self.state = States.DONE
            self.log_activity(self.task_activity_log_file, taskText, "DONE")
            
            # clears it
            self.activeTask = None
            self.entryTaskWidget.set_text("")
            
    def check_activity(self):
        activeWindow = get_active_window_title()
        idleTime = get_idle_time()
        if idleTime > self.settings['user_idle_threshold']:
            if not self.userIdle:
                self.log_activity(self.user_activity_log_file, "User", "IDLE")
                self.userIdle = True
        else:
            if self.userIdle:
                self.log_activity(self.user_activity_log_file, "User", "BACK")
                self.userIdle = False
                
        if self.lastActiveWindowTitle!=activeWindow:
            self.log_activity(self.user_activity_log_file, activeWindow, "ACTIVATED")
            self.lastActiveWindowTitle = activeWindow
            
        # This makes the timer to go on and on
        return True
         
   
    def delete_event(self, widget, event, data=None):
        # Change FALSE to TRUE and the main window will not be destroyed
        # with a "delete_event".
        return False

    def destroy(self, widget, data=None):
        if self.activeTask and self.state == States.STARTED:
            taskText = self.activeTask.verb+" "+self.activeTask.task
            self.state = States.STOPPED
            self.log_activity(self.task_activity_log_file, taskText, "STOPPED")
            
        if self.task_activity_log_file:
            self.task_activity_log_file.close()
        if self.user_activity_log_file:
            self.log_activity(self.user_activity_log_file, "Activity monitor", "OFFLINE")
            self.user_activity_log_file.close()
            gobject.source_remove(self.timer)
        gtk.main_quit()
        
    ## Member functions ##
    
    def __init__(self):
        #Set the Glade file
        self.gladefile = "taskSquashLite.glade"  
        self.wTree = gtk.Builder()
        self.wTree.add_from_file(self.gladefile)
        self.window = self.wTree.get_object("windowMain")
        
        if (self.window):
            dic = { "on_toolbuttonLater_clicked" : self.on_toolbuttonLater_clicked,
                    "on_toolbuttonDo_clicked" : self.on_toolbuttonDo_clicked,
                    "on_toolbuttonPause_clicked" : self.on_toolbuttonPause_clicked,
                    "on_toolbuttonDone_clicked" : self.on_toolbuttonDone_clicked,
                    "on_windowMain_destroy" : self.destroy}
            self.wTree.connect_signals(dic)

        self.entryTaskWidget = self.wTree.get_object("entryTask")
        self.doWidget = self.wTree.get_object("toolbuttonDo")    
        self.pauseWidget = self.wTree.get_object("toolbuttonPause")
        
        if (self.settings['keep_task_activity_log']):
            self.task_activity_log_file = open(self.settings['task_activity_log_file'], 'a')
        if (self.settings['keep_user_activity_log']):           
            uari = self.settings['user_activity_refresh_interval']
            self.timer = gobject.timeout_add(uari, self.check_activity)        
            self.user_activity_log_file = open(self.settings['user_activity_log_file'], 'a')
            self.log_activity(self.user_activity_log_file, "Activity monitor", "ONLINE")
            
        
        # and the window
        self.window.show()

    def main(self):
        gtk.main()

if __name__ == "__main__":
    app = TaskSquasherLiteWindow()
    app.main()