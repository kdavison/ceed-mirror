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

from PySide.QtGui import *
from PySide.QtCore import *

from xml.etree import ElementTree

import mixedtab

import undo
import xmledit

import PyCEGUI

class XMLEditing(xmledit.XMLEditWidget, mixedtab.EditMode):
    def __init__(self, parent):
        super(XMLEditing, self).__init__()
        
        self.parent = parent
        self.ignoreUndoCommands = False
        
        self.document().setUndoRedoEnabled(False)
        self.document().contentsChange.connect(self.slot_contentsChange)
        
    def refreshFromVisual(self):
        if not self.parent.visual.rootWidget:
            return
        
        source = PyCEGUI.WindowManager.getSingleton().getLayoutAsString(self.parent.visual.rootWidget)
        
        self.ignoreUndoCommands = True
        self.setPlainText(source)
        self.ignoreUndoCommands = False
        
    def propagateChangesToVisual(self):
        source = self.document().toPlainText()
        
        # for some reason, Qt calls hideEvent even though the tab widget was never shown :-/
        # in this case the source will be empty and parsing it will fail
        if source == "":
            return
        
        # TODO: What if this fails to parse? Do we show a message box that it failed and allow falling back
        #       to the previous visual state or do we somehow correct the XML like editors do?
        # we have to make the context the current context to ensure textures are fine
        self.parent.mainWindow.ceguiContainerWidget.makeGLContextCurrent()
        
        newRoot = PyCEGUI.WindowManager.getSingleton().loadLayoutFromString(source)
        self.parent.visual.replaceRootWidget(newRoot)
    
    def activate(self):
        super(XMLEditing, self).activate()
        self.refreshFromVisual()
        
    def deactivate(self):
        self.propagateChangesToVisual()
        
        return super(XMLEditing, self).deactivate()
    
    def slot_contentsChange(self, position, charsRemoved, charsAdded):
        #if not self.ignoreUndoCommands:
        #    totalChange = charsRemoved + charsAdded
        #    
        #    cmd = undo.XMLEditingCommand(self, self.lastUndoText, self.lastTextCursor,
        #                                       self.toPlainText(), self.textCursor(),
        #                                       totalChange)
        #    self.parent.undoStack.push(cmd)
        #    
        #self.lastUndoText = self.toPlainText()
        #self.lastTextCursor = self.textCursor()
        pass
        