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

def declare(actionManager):
    cat = actionManager.createCategory(name = "imageset", label = "Imageset Editor")
    
    cat.createAction(name = "edit_offsets", label = "Show and edit offsets",
                     help = "When you select an image, a crosshair will appear in it representing it's offset centrepoint..",
                     icon = QIcon("icons/imageset_editing/edit_offsets.png"),
                     defaultShortcut = QKeySequence(Qt.Key_Space)).setCheckable(True)
                     
    cat.createAction(name = "cycle_overlapping", label = "Cycle overlapping images",
                     help = "With some imagesets the inevitable will happen, their images will overlap in such a way that makes it hard/impossible to select the image you want, this allows you to select on of them and then just cycle until the right one is selected.",
                     icon = QIcon("icons/imageset_editing/cycle_overlapping.png"),
                     defaultShortcut = QKeySequence(Qt.Key_Q))
                     
    cat.createAction(name = "zoom_original", label = "Zoom original",
                     help = "Goes back to original 1:1 zoom.",
                     icon = QIcon("icons/imageset_editing/zoom_original.png"))
    
    cat.createAction(name = "zoom_in", label = "Zoom in",
                     help = "Zooms the whole imageset view closer (magnifying it by a factor of 2 from its current state).",
                     icon = QIcon("icons/imageset_editing/zoom_in.png"))
    
    cat.createAction(name = "zoom_out", label = "Zoom out",
                     help = "Zooms the whole imageset view further back (demagnifying it by a factor of 2 from its current state).",
                     icon = QIcon("icons/imageset_editing/zoom_out.png"))
    
    cat.createAction(name = "create_image", label = "Create image",
                     help = "Creates a new image at the current cursor position, sized 50x50 pixels.",
                     icon = QIcon("icons/imageset_editing/create_image.png"))
    
    cat.createAction(name = "duplicate_image", label = "Duplicate image",
                     help = "Duplicates the selected images.",
                     icon = QIcon("icons/imageset_editing/duplicate_image.png"))
    
    cat.createAction(name = "delete_image", label = "Delete image",
                     help = "Deletes all selected images.",
                     icon = QIcon("icons/imageset_editing/delete_image.png"))
    
    cat.createAction(name = "focus_image_list_filter_box", label = "Focus image list filter box",
                     help = "This allows you to easily press a shortcut and immediately search through images without having to reach for a mouse.",
                     icon = QIcon("icons/imageset_editing/focus_image_list_filter_box.png"),
                     defaultShortcut = QKeySequence(QKeySequence.Find))
