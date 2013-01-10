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
    import pango
except:
	sys.exit(1)
 
import SquasherConfig
import SquasherTasks


class ZimTaskSquasherWindow:
    
    
    ## Member variables ##

    tasksIn = []
    tasksDo = []
    tasksOut = []
    settings = SquasherConfig.defaultSettings
    
    
    ##  Member functions ##
    
    def load_task_list(self, filename):
        
        taskfile = open(filename, 'r')
        readtarget = None
        detailstarget = None
        
        tasksIn = []
        tasksDo = []
        tasksOut = []
        
        while 1:
            line = taskfile.readline()
            if not line:
                break

            if SquasherTasks.headerRe.search(line):
                readtarget = None
                detailstarget = None
                
                if self.settings["text_in_header"] in line:
                    readtarget = tasksIn
                elif self.settings["text_do_header"] in line:
                    readtarget = tasksDo
                elif self.settings["text_out_header"] in line:
                    readtarget = tasksOut
                
                continue
            
            # Check if the line contains a task  
            newTask = SquasherTasks.line_to_task(line)
            if newTask and readtarget!=None:
                readtarget.append(newTask)
                # Collect following lines detailing the task here
                detailstarget = newTask.details                
            
            # If there is active task details object. Pass all the following
            #  lines to its details field.
            elif readtarget!=None and detailstarget!=None:
                detailstarget.append(line)
                
        return tasksIn, tasksDo, tasksOut
    
    def save_task_list(self, filename):
        pass
    
    ## Ui handling helpers ##
    
    def update_lists(self):
        tasklists = [(self.tasksIn,self.inModel), 
                     (self.tasksDo,self.doModel),
                     (self.tasksOut,self.outModel)]
        
        dummyid = 0
        for tlist, tmodel in tasklists:
            tmodel.clear()
            for task in tlist:
                dummyid+=1
                
                # generate effort
                effortfield = ""
                effortfield+=str(task.effortReal) if task.effortReal else "?"
                effortfield+="/"
                effortfield+=str(task.effortEstimate) if task.effortEstimate else "?"
                
                # add data
                tmodel.append([
                    dummyid,
                    "%s %s" % (task.verb, task.task),
                    task.priority,
                    effortfield ])
                print "add data"
                    
            print tmodel

    ## Signal callback functions. ##
    
    def on_mcRevert_activate(self, widget, data=None):
        # Load data
        self.tasksIn, self.tasksDo, self.tasksOut = \
             self.load_task_list(self.settings["task_source_file"] )
        self.update_lists()
        
    def on_mcRefresh_activate(self, widget, data=None):
        pass
    def on_mcCommit_activate(self, widget, data=None):
        pass
        
    def on_toolbuttonAdd_clicked(self, widget, data=None):
        pass
    def on_toolbuttonReject_clicked(self, widget, data=None):
        pass
    def on_toolbuttonNext_clicked(self, widget, data=None):
        pass
    
    def on_toolbuttonLater_clicked(self, widget, data=None):
        pass
    def on_toolbuttonDo_clicked(self, widget, data=None):
        pass
    def on_toolbuttonPause_clicked(self, widget, data=None):
        pass
    def on_toolbuttonDone_clicked(self, widget, data=None):
        pass
    
    def on_toolbuttonRedo_clicked(self, widget, data=None):
        pass
    def on_toolbuttonHistory_clicked(self, widget, data=None):
        pass
    
    
    #PANGO_WRAP_WORD_CHAR
    
    def on_DescriptionColWidth_changed(self, column, width):
        # Fist children should be painter
        widthvalue = column.props.width
        renderer = column.get_cell_renderers()[0]
        renderer.set_property('wrap-width', widthvalue )
        renderer.set_property('wrap-mode', pango.WRAP_WORD_CHAR )    
   
    def delete_event(self, widget, event, data=None):
        # Change FALSE to TRUE and the main window will not be destroyed
        # with a "delete_event".
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def __init__(self):
        #Set the Glade file
        self.gladefile = "taskSquashWindow.glade"  
        self.wTree = gtk.Builder()
        self.wTree.add_from_file(self.gladefile)
        self.window = self.wTree.get_object ("windowMain")
        
        if (self.window):
            dic = { "on_mcRevert_activate" : self.on_mcRevert_activate,
                    "on_mcRefresh_activate" : self.on_mcRefresh_activate,
                    "on_mcCommit_activate" : self.on_mcCommit_activate,
                    "on_toolbuttonAdd_clicked" : self.on_toolbuttonAdd_clicked,
                    "on_toolbuttonReject_clicked" : self.on_toolbuttonReject_clicked,
                    "on_toolbuttonNext_clicked" : self.on_toolbuttonNext_clicked,
                    "on_toolbuttonLater_clicked" : self.on_toolbuttonLater_clicked,
                    "on_toolbuttonDo_clicked" : self.on_toolbuttonDo_clicked,
                    "on_toolbuttonPause_clicked" : self.on_toolbuttonPause_clicked,
                    "on_toolbuttonDone_clicked" : self.on_toolbuttonDone_clicked,
                    "on_toolbuttonRedo_clicked" : self.on_toolbuttonRedo_clicked,
                    "on_toolbuttonHistory_clicked" : self.on_toolbuttonHistory_clicked,
                    "on_windowMain_destroy" : self.destroy}
            self.wTree.connect_signals(dic)

            
        self.inModel = self.wTree.get_object('liststoreIn')
        self.doModel = self.wTree.get_object('liststoreDo')
        self.outModel = self.wTree.get_object('liststoreOut')
        
        
        defaultColumns = ['columnDescription1','columnDescription2','columnDescription3']
        for colname in defaultColumns:
            columnObject = self.wTree.get_object(colname)
            columnObject.connect("notify::width", self.on_DescriptionColWidth_changed)
        
        #gtk.TreeView.get_column()
        
        
        self.tasksIn, self.tasksDo, self.tasksOut = \
             self.load_task_list(self.settings["task_source_file"] )
        self.update_lists()
        
        # and the window
        self.window.show()

    def main(self):
        gtk.main()

if __name__ == "__main__":
    app = ZimTaskSquasherWindow()
    app.main()