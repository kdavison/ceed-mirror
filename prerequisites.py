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

"""
This module is used to check dependencies of CEED, check their versions
and provide helpful info when something goes wrong.
"""

def check(supressMessagesIfNotFatal = True):
    def messageBox(message):
        print message
    
    ret = True
    messages = []
    
    # Require python 2.6 or higher
    # NOTE: This is not necessarily required I think but I develop on 2.6 and 2.7
    import sys
    if sys.version_info < (2, 6):
        messages.append("Python is version '%s', at least 2.6 required" % (sys.version_info))
        ret = False
    
    # first we try PySide
    try:
        import PySide
        
    except ImportError:
        messages.append("PySide package is missing! PySide provides Python bindings for Qt4, see pyside.org")
        ret = False
        
    # we also check that PySide is at least version 1.0.3
    if PySide.__version_info__ < (1, 0, 3):
        messages.append("PySide package is not the required version (found version: '%s')! At least version 1.0.3 is required!" % (PySide.__version__))
        ret = False
        
    # next on the line is PyOpenGL
    try:
        import OpenGL.GL
        import OpenGL.GLU
        
    except ImportError:
        messages.append("PyOpenGL package is missing! PyOpenGL provides Python bindings for OpenGL, they can be found in the pypi repository.")
        ret = False
        
    # PyCEGUI is also required
    try:
        import PyCEGUI
        
    except ImportError:
        messages.append("PyCEGUI package is missing! PyCEGUI provides Python bindings for CEGUI, the library this editor edits assets for, see cegui.org.uk")
        ret = False
        
    if (not ret) or (not supressMessagesIfNotFatal and len(messages) > 0):
        messageBox("Following problems found: \n" + unicode("\n").join(messages))
    
    return ret