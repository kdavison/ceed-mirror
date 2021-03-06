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

from PySide import QtGui

from ceed.editors import multi

import PyCEGUI


class LookNFeelPreviewer(QtGui.QWidget, multi.EditMode):
    """Provides "Live Preview" which is basically interactive CEGUI rendering
    without any other outlines or what not over it.
    """

    def __init__(self, tabbedEditor):
        """
        :param tabbedEditor: LookNFeelTabbedEditor
        :return:
        """
        super(LookNFeelPreviewer, self).__init__()

        self.tabbedEditor = tabbedEditor
        self.rootWidget = None

        looknfeel = QtGui.QVBoxLayout(self)
        looknfeel.setContentsMargins(0, 0, 0, 0)
        self.setLayout(looknfeel)

    def activate(self):
        super(LookNFeelPreviewer, self).activate()

        assert(self.rootWidget is None)

        # we have to make the context the current context to ensure textures are fine
        mainwindow.MainWindow.instance.ceguiContainerWidget.makeGLContextCurrent()

        currentRootWindow = self.tabbedEditor.visual.rootWindow
        if currentRootWindow is None:
            self.rootWidget = None

        else:
            # lets clone so we don't affect the Look n' Feel at all
            self.rootWidget = currentRootWindow.clone()

        PyCEGUI.System.getSingleton().getDefaultGUIContext().setRootWindow(self.rootWidget)

    def deactivate(self):
        if self.rootWidget is not None:
            PyCEGUI.WindowManager.getSingleton().destroyWindow(self.rootWidget)
            self.rootWidget = None

        return super(LookNFeelPreviewer, self).deactivate()

    def showEvent(self, event):
        super(LookNFeelPreviewer, self).showEvent(event)

        mainwindow.MainWindow.instance.ceguiContainerWidget.activate(self)
        # we always want continuous rendering in live preview
        mainwindow.MainWindow.instance.ceguiContainerWidget.setViewFeatures(continuousRendering = True)
        mainwindow.MainWindow.instance.ceguiContainerWidget.enableInput()

        if self.rootWidget:
            PyCEGUI.System.getSingleton().getDefaultGUIContext().setRootWindow(self.rootWidget)

    def hideEvent(self, event):
        mainwindow.MainWindow.instance.ceguiContainerWidget.disableInput()
        mainwindow.MainWindow.instance.ceguiContainerWidget.deactivate(self)

        if self.rootWidget:
            PyCEGUI.System.getSingleton().getDefaultGUIContext().setRootWindow(None)

        super(LookNFeelPreviewer, self).hideEvent(event)

# needs to be at the end, import to get the singleton
from ceed import mainwindow
