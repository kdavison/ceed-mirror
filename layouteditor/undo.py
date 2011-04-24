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

import commands

idbase = 1200

class MoveCommand(commands.UndoCommand):
    """This command simply moves given widgets from old positions to new
    """
    
    def __init__(self, visual, widgetPaths, oldPositions, newPositions):
        super(MoveCommand, self).__init__()
        
        self.visual = visual
        
        self.widgetPaths = widgetPaths
        self.oldPositions = oldPositions
        self.newPositions = newPositions
    
        self.refreshText()
    
    def refreshText(self):            
        if len(self.widgetPaths) == 1:
            self.setText("Move '%s'" % (self.widgetPaths[0]))
        else:
            self.setText("Move %i widgets" % (len(self.widgetPaths)))
                
    def id(self):
        return idbase + 1
        
    def mergeWith(self, cmd):
        if self.widgetPaths == cmd.widgetPaths:
            # TODO
        
            pass
        
        return False
        
    def undo(self):
        super(MoveCommand, self).undo()
        
        for widgetPath in self.widgetPaths:
            widgetManipulator = self.visual.scene.getWidgetManipulatorByPath(widgetPath)
            widgetManipulator.widget.setPosition(self.oldPositions[widgetPath])
            widgetManipulator.updateFromWidget()
            
    def redo(self):
        for widgetPath in self.widgetPaths:
            widgetManipulator = self.visual.scene.getWidgetManipulatorByPath(widgetPath)
            widgetManipulator.widget.setPosition(self.newPositions[widgetPath])
            widgetManipulator.updateFromWidget()
            
        super(MoveCommand, self).redo()

class ResizeCommand(commands.UndoCommand):
    """This command resizes given widgets from old positions and old sizes to new
    """
    
    def __init__(self, visual, widgetPaths, oldPositions, oldSizes, newPositions, newSizes):
        super(ResizeCommand, self).__init__()
        
        self.visual = visual
        
        self.widgetPaths = widgetPaths
        self.oldPositions = oldPositions
        self.oldSizes = oldSizes
        self.newPositions = newPositions
        self.newSizes = newSizes
    
        self.refreshText()
    
    def refreshText(self):            
        if len(self.widgetPaths) == 1:
            self.setText("Resize '%s'" % (self.widgetPaths[0]))
        else:
            self.setText("Resize %i widgets" % (len(self.widgetPaths)))
                
    def id(self):
        return idbase + 2
        
    def mergeWith(self, cmd):
        if self.widgetPaths == cmd.widgetPaths:
            # TODO
        
            pass
        
        return False
        
    def undo(self):
        super(ResizeCommand, self).undo()
        
        for widgetPath in self.widgetPaths:
            widgetManipulator = self.visual.scene.getWidgetManipulatorByPath(widgetPath)
            widgetManipulator.widget.setPosition(self.oldPositions[widgetPath])
            widgetManipulator.widget.setSize(self.oldSizes[widgetPath])
            widgetManipulator.updateFromWidget()
            
    def redo(self):
        for widgetPath in self.widgetPaths:
            widgetManipulator = self.visual.scene.getWidgetManipulatorByPath(widgetPath)
            widgetManipulator.widget.setPosition(self.newPositions[widgetPath])
            widgetManipulator.widget.setSize(self.newSizes[widgetPath])
            widgetManipulator.updateFromWidget()
            
        super(ResizeCommand, self).redo()

class PropertyEditCommand(commands.UndoCommand):
    """This command resizes given widgets from old positions and old sizes to new
    """
    
    def __init__(self, visual, propertyName, widgetPaths, oldValues, newValue):
        super(PropertyEditCommand, self).__init__()
        
        self.visual = visual
        
        self.propertyName = propertyName
        self.widgetPaths = widgetPaths
        self.oldValues = oldValues
        self.newValue = newValue
        
        self.refreshText()
    
    def refreshText(self):            
        if len(self.widgetPaths) == 1:
            self.setText("Change '%s' in '%s'" % (self.propertyName, self.widgetPaths[0]))
        else:
            self.setText("Change '%s' in %i widgets" % (self.propertyName, len(self.widgetPaths)))
        
    def id(self):
        return idbase + 3
        
    def mergeWith(self, cmd):
        if self.widgetPaths == cmd.widgetPaths:
            # TODO
        
            pass
        
        return False
        
    def undo(self):
        super(PropertyEditCommand, self).undo()
        
        for widgetPath in self.widgetPaths:
            widgetManipulator = self.visual.scene.getWidgetManipulatorByPath(widgetPath)
            widgetManipulator.widget.setProperty(self.propertyName, self.oldValues[widgetPath])
            widgetManipulator.updateFromWidget()
            
    def redo(self):
        for widgetPath in self.widgetPaths:
            widgetManipulator = self.visual.scene.getWidgetManipulatorByPath(widgetPath)
            widgetManipulator.widget.setProperty(self.propertyName, self.newValue)
            widgetManipulator.updateFromWidget()
            
        super(PropertyEditCommand, self).redo()