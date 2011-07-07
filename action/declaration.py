################################################################################
#   CEED - A unified CEGUI editor
#   Copyright (C) 2011 Martin Preisler <preisler.m@gmail.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

from PySide.QtCore import *
from PySide.QtGui import *

class Action(QAction):
    """The only thing different in this from QAction is the ability to change the shortcut of it
    using CEED's settings API/interface.
    
    While it isn't needed/required to use this everywhere where QAction is used, it is recommended.
    """
    
    def __init__(self, category, name, label = None, icon = QIcon(), defaultShortcut = QKeySequence()):
        if label is None:
            label = name
            
        self.category = category
        self.name = name
        self.defaultShortcut = defaultShortcut
        
        # QAction needs a QWidget parent, we use the main window as that
        super(Action, self).__init__(icon, label, self.getManager().mainWindow)
        
        self.setShortcut(defaultShortcut)
        
        self.settingsEntry = None
        self.declareSettingsEntry()
        
    def getManager(self):
        return self.category.manager
    
    def declareSettingsEntry(self):
        section = self.category.settingsSection
        
        self.settingsEntry = section.addEntry(name = "shortcut_%s" % (self.name), type = QKeySequence, label = "Shortcut for %s ('%s')" % (self.label, self.name),
                                              defaultValue = self.defaultShortcut, widgetHint = "keySequence")

class ActionCategory(object):
    def __init__(self, manager, name, label = None):
        if label is None:
            label = name
            
        self.manager = manager
        self.name = name
        self.label = label
        
        self.settingsSection = None
        self.declareSettingsSection()
    
    def getManager(self):
        return self.manager
    
    def createAction(self, **kwargs):
        action = Action(self, **kwargs)
        self.actions.append(action)
        
        return action

    def setEnabled(self, enabled):
        """Allows you to enable/disable actions en masse, especially useful when editors are switched.
        This gets rid of shortcut clashes and so on.
        """
        
        for action in self.actions:
            action.setEnabled(enabled)

    def declareSettingsSection(self):
        category = self.getManager().settingsCategory
        
        self.settingsSection = category.addSection(name = self.name, label = self.label)

class ActionManager(object):
    def __init__(self, mainWindow, settings):
        self.mainWindow = mainWindow
        self.settings = settings
        
        self.settingsCategory = None
        self.declareSettingsCategory()
    
    def createCategory(self, **kwargs):
        category = ActionCategory(self, **kwargs)
        self.categories.append(category)
        
        return category
    
    def declareSettingsCategory(self):
        self.settingsCategory = self.settings.addCategory(name = "action_shortcuts", label = "Shortcuts", sortingWeight = 999)
    