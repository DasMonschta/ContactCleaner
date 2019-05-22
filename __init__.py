from ts3plugin import ts3plugin
import ts3defines, os.path
import ts3lib as ts3
from ts3lib import getPluginPath
from os import path
from PythonQt.QtCore import *
from PythonQt.QtSql import QSqlDatabase
from PythonQt.QtGui import *
from pytsonui import *
import datetime
            
class AvatarCollector(ts3plugin):
    name            = "Contact Cleaner"
    requestAutoload = False
    version         = "1.0"
    apiVersion      = 21
    author          = "Luemmel"
    description     = "Delete contacts which you haven't seen for the selected time."
    offersConfigure = True
    commandKeyword  = ""
    infoTitle       = None
    hotkeys         = []
    menuItems       = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Contace Cleaner", "")]
    ac              = None
    
    def __init__(self):        
        pass
        
    def stop(self):
        pass
        
    def configure(self, qParentWidget):
        self.ac = Dialog(self)
        self.ac.show()
        
    def onMenuItemEvent(self, sch_id, a_type, menu_item_id, selected_item_id):
        if a_type == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
            if menu_item_id == 0:               
                self.ac = Dialog(self)
                self.ac.show()     

class Dialog(QDialog):    

    def __init__(self, cc, parent=None):      
        self.cc = cc
        super(QDialog, self).__init__(parent)       
        self.setWindowIcon(QIcon(os.path.join(getPluginPath(), "pyTSon", "scripts", "contactcleaner", "icon.png")))
        setupUi(self, os.path.join(getPluginPath(), "pyTSon", "scripts", "contactcleaner", "main.ui"))
        self.setWindowTitle("Contact Cleaner")
        
        # Load version from plguin vars
        self.ui_label_version.setText("v"+cc.version)
        
        # Delete QDialog on Close
        self.setAttribute(Qt.WA_DeleteOnClose)

        # Disable help button
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)        

        # Button connects
        self.ui_btn_check.clicked.connect(self.check)
        self.ui_btn_clean.clicked.connect(self.clean)
        
        # Current time
        self.datenow_obj = datetime.datetime.now()
        
        # Add options to combo
        self.ui_combo_time.addItem("1 month", 1)
        self.ui_combo_time.addItem("3 month", 3)
        self.ui_combo_time.addItem("6 month", 6)
        self.ui_combo_time.addItem("1 year", 12)
        self.ui_combo_time.addItem("2 years", 24)
        self.ui_combo_time.addItem("3 years amd more", 36)
        
    def check(self):      
        # keys array
        self.keys = []
        
        # Select all colums from contacts
        db = ts3client.Config()        
        q = db.query("SELECT * FROM contacts")
        
        # While rows
        while q.next():             
            # Split value string on new line
            val = q.value("value").split('\n')
            
            # For each line check if starts with LastSeen=
            for line in val:
                if line.startswith('LastSeen='):
                
                    # Split line to get date
                    lastseen = line.split('LastSeen=')[1]
                    
                    # if empty then put key into keys and goto next row
                    if lastseen == "": 
                        self.keys.append(q.value("key"))
                        continue
                        
                    # create date obj from date string    
                    lastseen_obj = datetime.datetime.strptime(lastseen, "%Y-%m-%dT%H:%M:%S")          
 
                    # difference between now and lastseen
                    difference = self.datenow_obj - lastseen_obj

                    # if difference bigger than selected time then put key into ekys
                    if (self.ui_combo_time.currentData * 30) <= difference.days:
                        self.keys.append(q.value("key"))                      
        
        # update selected users label
        self.ui_label_selected.setText("Selected users: "+str(len(self.keys)))
        
    def clean(self):       
        # if keys not empty
        if self.keys:
        
            # convert keys array to string seperated by ,
            seperator = ", "
            key_string = seperator.join(self.keys)
            
            # delete data
            db = ts3client.Config()        
            q = db.query("DELETE FROM contacts WHERE key in ("+key_string+")")
            
            # crash teamspeak to make delete effective
            qFatal("boom")



           