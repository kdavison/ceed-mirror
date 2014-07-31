##############################################################################
#   CEED - Unified CEGUI asset editor
#
#   Copyright (C) 2011-2012   Martin Preisler <martin@preisler.me>
#                             and contributing authors (see AUTHORS file)
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
##############################################################################

from ceed import commands

from ceed.editors.looknfeel import widgethelpers
import PyCEGUI

idbase = 1300


class TargetWidgetChangeCommand(commands.UndoCommand):
    """This command changes the Look n' Feel widget targeted for editing to another one
    """

    def __init__(self, visual, tabbedEditor, newTargetWidgetLook):
        """
        :param visual: LookNFeelVisualEditing
        :param tabbedEditor: LookNFeelTabbedEditor
        :param newTargetWidgetLook: string
        :return:
        """
        super(TargetWidgetChangeCommand, self).__init__()

        self.visual = visual
        self.tabbedEditor = tabbedEditor
        self.oldTargetWidgetLook = tabbedEditor.targetWidgetLook
        self.newTargetWidgetLook = newTargetWidgetLook

        self.refreshText()

    def refreshText(self):
        self.setText("Change the target of Look n' Feel editing from widget \"" + self.oldTargetWidgetLook + "\" to \"" + self.newTargetWidgetLook + "\"")

    def id(self):
        return idbase + 1

    def mergeWith(self, cmd):
        return False

    def undo(self):
        super(TargetWidgetChangeCommand, self).undo()

        self.tabbedEditor.targetWidgetLook = self.oldTargetWidgetLook
        self.tabbedEditor.visual.displayNewTargetWidgetLook()

        if self.tabbedEditor.targetWidgetLook == "":
            self.visual.falagardElementEditorDockWidget.inspector.setSource(None)
        else:
            widgetLookObject = PyCEGUI.WidgetLookManager.getSingleton().getWidgetLook(self.tabbedEditor.targetWidgetLook)
            self.visual.falagardElementEditorDockWidget.inspector.setSource(widgetLookObject)

        self.visual.lookNFeelHierarchyDockWidget.updateToNewWidgetLook()

    def redo(self):
        self.tabbedEditor.targetWidgetLook = self.newTargetWidgetLook
        self.visual.displayNewTargetWidgetLook()

        if self.tabbedEditor.targetWidgetLook == "":
            self.visual.falagardElementEditorDockWidget.inspector.setSource(None)
        else:
            widgetLookObject = PyCEGUI.WidgetLookManager.getSingleton().getWidgetLook(self.tabbedEditor.targetWidgetLook)
            self.visual.falagardElementEditorDockWidget.inspector.setSource(widgetLookObject)

        self.visual.lookNFeelHierarchyDockWidget.updateToNewWidgetLook()

        super(TargetWidgetChangeCommand, self).redo()


class FalagardElementAttributeEdit(commands.UndoCommand):
    """This command resizes given widgets from old positions and old sizes to new
    """

    def __init__(self, visual, falagardElement, attributeName, newValue, ignoreNextCallback=False):
        super(FalagardElementAttributeEdit, self).__init__()

        self.visual = visual

        self.falagardElement = falagardElement
        self.attributeName = attributeName
        from falagard_element_interface import FalagardElementInterface
        self.oldValue = FalagardElementInterface.getAttributeValue(falagardElement, attributeName)
        self.newValue = newValue

        self.refreshText()

        self.ignoreNextCallback = ignoreNextCallback

    def refreshText(self):
        if len(self.widgetPaths) == 1:
            self.setText("Change '%s' in '%s'" % (self.propertyName, self.widgetPaths[0]))
        else:
            self.setText("Change '%s' in %i widgets" % (self.propertyName, len(self.widgetPaths)))

    def id(self):
        return idbase + 2

    def mergeWith(self, cmd):
        return False

    def undo(self):
        super(FalagardElementAttributeEdit, self).undo()

        from falagard_element_interface import FalagardElementInterface
        FalagardElementInterface.setAttributeValue(self.falagardElement, self.attributeName, self.oldValue)

        # make sure to redraw the scene so the changes are visible
        self.visual.scene.update()

    def redo(self):
        from falagard_element_interface import FalagardElementInterface
        FalagardElementInterface.setAttributeValue(self.falagardElement, self.attributeName, self.newValue)

        # make sure to redraw the scene so the changes are visible
        self.visual.scene.update()

        super(FalagardElementAttributeEdit, self).redo()