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

import datetime
import os.path
from collections import defaultdict
 
import SquasherConfig
import SquasherTasks

from ActiveWindow import get_active_window_title
from WindowsIdle import get_idle_time
from NagDetector import test_if_should_nag, teach_classifiers, verify_classifiers

## Data structures etc. ##

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)
States = enum('WAIT_NEW', 'STARTED', 'PAUSED', 'STOPPED')  
        
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
    teaching = False
    
    # Nagging classifiers 
    nagssifiers = None
    
    ## Helper methods ##
    
    @staticmethod
    def log_activity(logfile, task, activity):
        if logfile:
            dtstamp = datetime.datetime.now()
            act = "%s\t%s\t%s\n" % (dtstamp.isoformat(), activity.upper(), task) 
            logfile.write(act)
            
    def update_button_states(self, state=None):
        if state==None:
            state = self.state
            
        self.workaround_block_signals = True
        
        if (state==States.WAIT_NEW):     
            self.doWidget.set_active(False)
            self.pauseWidget.set_active(False)
            self.entryTaskWidget.set_sensitive(True)
        elif (state==States.STARTED):
            self.doWidget.set_active(True)
            self.pauseWidget.set_active(False)
            self.entryTaskWidget.set_sensitive(False)
        elif (state==States.PAUSED):
            self.doWidget.set_active(True)
            self.pauseWidget.set_active(True)
            self.entryTaskWidget.set_sensitive(False)
        elif (state==States.STOPPED):
            self.doWidget.set_active(False)
            self.pauseWidget.set_active(False)
            self.entryTaskWidget.set_sensitive(False)
            
        if self.settings['nag']:
            if self.teaching:
                self.teachWidget.set_active(True)
            else:
                self.teachWidget.set_active(False)
        else:
            self.teachWidget.set_sensitive(False)
        
        self.workaround_block_signals = False
    
    def nag(self):
        md = gtk.MessageDialog(self.window, 
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING, 
            gtk.BUTTONS_OK, "Slacker!")
        md.run()
        md.destroy()
        
    ## Signal callback functions. ##
    
    def on_toolbuttonLater_clicked(self, widget, data=None):
        # Stop active task
        if self.activeTask:
            taskText = self.activeTask.verb+" "+self.activeTask.task
            if self.state == States.STARTED:
                self.log_activity(self.task_activity_log_file, taskText, "STOPPED")
            self.log_activity(self.task_activity_log_file, taskText, "POSTPONED")
            
        self.activeTask = None
        # clears it
        self.entryTaskWidget.set_text("")
        self.state = States.WAIT_NEW
        
        # Make sure UI is in right state
        self.update_button_states()
        
        
    def on_toolbuttonDo_clicked(self, widget, data=None):
        if self.workaround_block_signals:
            return
       
        # It is already being squashed!
        if self.state == States.STARTED or self.state == States.PAUSED:
            self.update_button_states()
            return

        taskLine = self.entryTaskWidget.get_text()        
        task = SquasherTasks.line_to_task(taskLine)
        
        if self.settings['require_zim_task_format'] and not task:
            md = gtk.MessageDialog(self.window, 
                gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, 
                gtk.BUTTONS_CLOSE, "Task is not of Zim format")
            md.run()
            md.destroy()
        else:            
            if self.settings['encourage_use_of_verb_tag'] and \
               (len(task.tags)==0 or task.verb!=task.tags[0]):
                md = gtk.MessageDialog(self.window, 
                gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, 
                gtk.BUTTONS_YES_NO, 
                    r"""Consider @Using a tag as the task verb (first word of the task).
                    Do you want to change it now?""")
                if md.run()==gtk.RESPONSE_YES:
                    # Abort action
                    md.destroy()  
                    self.update_button_states()
                    return
                else:
                    md.destroy()
                
            self.activeTask = task
            taskText = self.activeTask.verb+" "+self.activeTask.task
            self.state = States.STARTED
            self.log_activity(self.task_activity_log_file, taskText, "STARTED")
        
        # Make sure UI is in right state        
        self.update_button_states()
       
    def on_toolbuttonPause_clicked(self, widget, data=None):
        if self.workaround_block_signals:
            return
            
        if self.activeTask:            
            taskText = self.activeTask.verb+" "+self.activeTask.task
            
            if self.state == States.STARTED:
                self.state = States.PAUSED
                self.log_activity(self.task_activity_log_file, taskText, "STOPPED")
            # From paused state to started
            elif self.state == States.PAUSED:
                self.state = States.STARTED
                self.log_activity(self.task_activity_log_file, taskText, "STARTED")
        
        # Make sure UI is in right state
        self.update_button_states()
    
            
    def on_toolbuttonDone_clicked(self, widget, data=None):
        if not self.activeTask:
            return
            
        taskText = self.activeTask.verb+" "+self.activeTask.task
        
        if self.state == States.STARTED:
            # For easier parsing, go to DONE trough STOPPED
            self.log_activity(self.task_activity_log_file, taskText, "STOPPED")            
        
        self.log_activity(self.task_activity_log_file, taskText, "DONE")
            
        # clears it
        self.state = States.WAIT_NEW
        self.activeTask = None
        self.entryTaskWidget.set_text("")
        
        # Make sure UI is in right state
        self.update_button_states()
        
    def on_toolbuttonTeach_clicked(self, widget, data=None):
        if self.workaround_block_signals:
            return        
        # Toggle state
        self.teaching = not self.teaching
        
    def check_activity(self):
        activeWindow = get_active_window_title()
        idleTime = get_idle_time()
        
        if activeWindow=="":
            activeWindow = "-"
        
        # Check for user idle
        if idleTime > self.settings['user_idle_threshold']:
            if not self.userIdle:
                self.log_activity(self.user_activity_log_file, "User", "IDLE")
                self.userIdle = True
        else:
            if self.userIdle:
                self.log_activity(self.user_activity_log_file, "User", "BACK")
                self.userIdle = False
        
        # Log active window
        if self.lastActiveWindowTitle!=activeWindow:
            self.log_activity(self.user_activity_log_file, activeWindow, "ACTIVATED")
            self.lastActiveWindowTitle = activeWindow
        
            if self.settings['nag']:
                # Teach active window to be specific for current task (or lack of)
                if self.teaching and self.nag_teach_file:
                    activeTags = []
                    if self.activeTask:
                        activeTags = self.activeTask.tags
                    self.log_activity(self.nag_teach_file, activeWindow, str(activeTags))
                elif self.activeTask and self.state == States.STARTED:
                    doNag = test_if_should_nag(
                        self.nagssifiers, self.activeTask.tags,
                        activeWindow, self.settings['nag_require_all_tags'])
                    if doNag:
                        self.nag()
                        
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
        if self.nag_teach_file:
            self.nag_teach_file.close()
        gtk.main_quit()
        
    ## Member functions ##
    
    def __init__(self):
        #Set the Glade file
        self.gladefile = "taskSquashLite.glade"  
        self.wTree = gtk.Builder()
        self.wTree.add_from_file(self.gladefile)
        self.window = self.wTree.get_object("windowMain")
        
        if (self.window):
            dic = { 'on_toolbuttonLater_clicked' : self.on_toolbuttonLater_clicked,
                    'on_toolbuttonDo_clicked' : self.on_toolbuttonDo_clicked,
                    'on_toolbuttonPause_clicked' : self.on_toolbuttonPause_clicked,
                    'on_toolbuttonDone_clicked' : self.on_toolbuttonDone_clicked,
                    'on_toolbuttonTeach_clicked' : self.on_toolbuttonTeach_clicked,
                    'on_windowMain_destroy' : self.destroy}
            self.wTree.connect_signals(dic)

        self.entryTaskWidget = self.wTree.get_object("entryTask")
        self.doWidget = self.wTree.get_object("toolbuttonDo")    
        self.pauseWidget = self.wTree.get_object("toolbuttonPause")
        self.teachWidget = self.wTree.get_object("toolbuttonTeach")
        self.statusBar = self.wTree.get_object("statusbar")
        
        if (self.settings['keep_task_activity_log']):
            self.task_activity_log_file = open(self.settings['task_activity_log_file'], 'a+')
        if (self.settings['keep_user_activity_log']):           
            uari = self.settings['user_activity_refresh_interval']
            self.timer = gobject.timeout_add(uari, self.check_activity)        
            self.user_activity_log_file = open(self.settings['user_activity_log_file'], 'a+')
            self.log_activity(self.user_activity_log_file, "Activity monitor", "ONLINE")
            
        if self.settings['nag']:
            nagfn = self.settings['nag_teach_file']
            if os.path.isfile(nagfn):
                self.nagssifiers = teach_classifiers(nagfn)
                verify_classifiers(self.nagssifiers, nagfn, verbose=2)
            
            # Open for possible additional teaching
            self.nag_teach_file = open(nagfn, 'a+')
            
        # and the window
        self.window.show()

    def main(self):
        gtk.main()

if __name__ == "__main__":
    app = TaskSquasherLiteWindow()
    app.main()