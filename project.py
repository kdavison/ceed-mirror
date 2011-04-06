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

import os
import sys

from xml.etree import ElementTree

import qtwidgets

import ui.projectmanager
import ui.newprojectdialog
import ui.projectsettingsdialog

class Item(QStandardItem):
    """One item in the project
    This is usually a file or a folder
    """
    
    Unknown = 1
    """A file is an item that can't have any children, it is directly opened instead of
    being expanded/collapsed like folders
    """
    File = 2
    Folder = 3

    itemType = property(lambda self: self.data(Qt.UserRole + 1),
                    lambda self, value: self.setItemType(value))
    
    label = property(lambda self: self.text(),
                     lambda self, value: self.setText(value))
    
    icon = property(lambda self: self.icon(),
                    lambda self, value: self.setIcon(QIcon(value)))
    
    # only applicable to files
    """path is the path relative to project's base dir"""
    path = property(lambda self: self.getPath(),
                    lambda self, value: self.setPath(value))
    # only applicable to folders
    name = property(lambda self: self.getName(),
                    lambda self, value: self.setName(value))
        
    def __init__(self, project):
        super(Item, self).__init__()
        
        self.project = project
        self.itemType = Item.Unknown
        
        self.project.changed = True
    
    def type(self):
        # Qt docs say we have to overload type() and return something > QStandardItem.UserType
        return QStandardItem.UserType + 1
    
    def clone(self):
        ret = Item(self.project)
        ret.itemType = self.itemType
        
        if self.itemType == Item.File:
            ret.path = self.path
        
        elif self.itemType == Item.Folder:
            ret.name = self.name
            
        else:
            pass
        
        # PySide bug: PySide doesn't take ownership so we have to hack this around like this
        #             hopefully this gets fixed.
        #
        #             NASTY NASTY NASTY
        if hasattr(self, "returnedClones"):
            self.returnedClones.append(ret)
        else:
            self.returnedClones = [ret]
              
        return ret
    
    def setItemType(self, value):
        self.setData(value, Qt.UserRole + 1)
        
        if value == Item.File:
            self.setDragEnabled(True)
            self.setDropEnabled(False)
            
        elif value == Item.Folder:
            self.setDragEnabled(True)
            self.setDropEnabled(True)
        
        else:
            self.setDragEnabled(False)
            self.setDropEnabled(False)
    
    def setPath(self, value):
        assert(self.itemType == Item.File)
        
        self.setData(value, Qt.UserRole + 2)
        self.label = os.path.basename(value)
       
        # TODO: File type icons are completely independent from tabbed editors,
        #       do we want to couple them or not?
        #
        #       Project management right now has no idea about mainwindow
        #       or tabbed editing (and that's a good thing IMO)
            
        fileType = "unknown"
        if value.endswith(".font"):
            fileType = "font"
        elif value.endswith(".layout"):
            fileType = "layout"
        elif value.endswith(".imageset"):
            fileType = "imageset"
        elif value.endswith(".anim"):
            fileType = "animation"
        elif value.endswith(".scheme"):
            fileType = "scheme"
        elif value.endswith(".looknfeel"):
            fileType = "looknfeel"
        elif value.endswith(".py"):
            fileType = "python_script"
        elif value.endswith(".lua"):
            fileType = "lua_script"
        elif value.endswith(".xml"):
            fileType = "xml"
        elif value.endswith(".txt"):
            fileType = "text"
        else:
            extensions = [".png", ".jpg", ".jpeg", ".tga", ".dds"]
            
            for extension in extensions:
                if value.endswith(extension):
                    fileType = "bitmap"
                    break
            
        self.icon = "icons/project_items/%s.png" % (fileType)
        
        self.project.changed = True
            
    def getPath(self):
        assert(self.itemType == Item.File)
        
        return self.data(Qt.UserRole + 2)
    
    def setName(self, value):
        assert(self.itemType == Item.Folder)
        
        self.setData(value, Qt.UserRole + 2)
        
        # A hack to cause folders appear first when sorted
        # TODO: Override the sorting method and make this work more cleanly
        self.label = " %s" % (value)
        self.icon = "icons/project_items/folder.png"
        
        self.project.changed = True
        
    def getName(self):
        assert(self.itemType == Item.Folder)
        
        return self.data(Qt.UserRole + 2)
    
    def getRelativePath(self):
        """Returns path relative to the projects base directory"""
        assert(self.itemType == Item.File)
        
        return self.path
    
    def getAbsolutePath(self):
        assert(self.itemType == Item.File)
        
        return self.project.getAbsolutePathOf(self.path)
        
    @staticmethod
    def loadFromElement(project, parent, element):
        item = Item(project)
        
        typeString = element.get("type")
        if typeString == "file":
            item.itemType = Item.File
            item.path = element.get("path")
            
        elif typeString == "folder":
            item.itemType = Item.Folder
            item.name = element.get("name")
            
            subItemElements = element.findall("Item")
            for subItemElement in subItemElements:
                subItem = Item.loadFromElement(project, item, subItemElement)
                item.appendRow(subItem)
                
        else:
            raise Exception("Unknown item type '%s'" % (type))
            
        return item
    
    def saveToElement(self):
        ret = ElementTree.Element("Item")
        
        if self.itemType == Item.File:
            ret.set("type", "file")
            ret.set("path", self.path)
            
        elif self.itemType == Item.Folder:
            ret.set("type", "folder")
            ret.set("name", self.name)
            
            i = 0
            while i < self.rowCount():
                subItemElement = self.child(i).saveToElement()
                ret.append(subItemElement)
                i = i + 1
                
        return ret

class Project(QStandardItemModel):
    """This class encapsulates a project edited by the editor

    A project is basically a set of files and folders that are CEGUI related
    (.font, .layout, ...)
    """
    
    def __init__(self):
        super(Project, self).__init__()
        
        self.setHorizontalHeaderLabels(["Name"])
        self.setSupportedDragActions(Qt.MoveAction)
        self.prototype = Item(self)
        self.setItemPrototype(self.prototype)
        
        self.name = "Unknown"
        self.projectFilePath = ""
        self.baseDirectory = "./"
        
        self.imagesetsPath = "./imagesets"
        self.fontsPath = "./fonts"
        self.looknfeelsPath = "./looknfeel"
        self.schemesPath = "./schemes"
        self.layoutsPath = "./layouts"
        
        self.changed = True

    def getSupportedDropActions(self):
        return Qt.MoveAction

    def load(self, path):
        """Loads XML project file from given path (preferably absolute path)"""
        
        tree = ElementTree.parse(path)
        root = tree.getroot()
        
        assert(root.get("version") == "0.8")
        
        self.name = root.get("name", "Unknown")
            
        self.baseDirectory = root.get("base_directory", "./")
        
        self.imagesetsPath = root.get("imagesets_path", "./imagesets")            
        self.fontsPath = root.get("fonts_path", "./fonts")            
        self.looknfeelsPath = root.get("looknfeels_path", "./looknfeel")            
        self.schemesPath = root.get("schemes_path", "./schemes")            
        self.layoutsPath = root.get("layouts_path", "./layouts")
        
        items = root.find("Items")
        
        for itemElement in items.findall("Item"):
            item = Item.loadFromElement(self, None, itemElement)
            self.appendRow(item)
            
        self.changed = False
        self.projectFilePath = path

    def unload(self):
        pass

    def save(self, path = ""):
        if path == "":
            path = self.projectFilePath
            self.changed = False
        
        root = ElementTree.Element("Project")
        
        # This CEED is built to conform CEGUI 0.8
        root.set("version", "0.8")
        root.set("name", self.name)
        root.set("base_directory", self.baseDirectory)
        
        root.set("imagesets_path", self.imagesetsPath)
        root.set("fonts_path", self.fontsPath)
        root.set("looknfeels_path", self.looknfeelsPath)
        root.set("schemes_path", self.schemesPath)
        root.set("layouts_path", self.layoutsPath)
        
        items = ElementTree.SubElement(root, "Items")
        
        i = 0
        while i < self.rowCount():
            items.append(self.item(i).saveToElement())
            i = i + 1
        
        tree = ElementTree.ElementTree(root)
        tree.write(path)
    
    def hasChanges(self):
        return self.changed

    def getAbsolutePathOf(self, path):
        """Converts project relative paths to absolute paths"""
 
        absoluteBaseDirectory = os.path.join(os.path.dirname(self.projectFilePath), self.baseDirectory)
        return os.path.normpath(os.path.join(absoluteBaseDirectory, path))
    
    def getRelativePathOf(self, path):
        return os.path.normpath(os.path.relpath(path, os.path.abspath(os.path.dirname(self.projectFilePath))))

class ProjectManager(QDockWidget):
    """This is basically a view of the Project model class,
    it allows browsing and (in the future) changes
    """
    
    project = property(lambda self: self.view.model(),
                       lambda self, value: self.setProject(value))
    
    fileOpenRequested = Signal(str)
    
    def __init__(self):
        super(ProjectManager, self).__init__()
        
        self.ui = ui.projectmanager.Ui_ProjectManager()
        self.ui.setupUi(self)
        
        self.view = self.findChild(QTreeView, "view")
        self.view.sortByColumn(0, Qt.AscendingOrder)
        self.view.doubleClicked.connect(self.slot_itemDoubleClicked)
        
        self.setupContextMenu()
        
        self.setProject(None)
        
    def setupContextMenu(self):
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        
        self.contextMenu = QMenu(self)
        
        self.createFolderAction = QAction(QIcon("icons/project_management/create_folder.png"), "Create folder", self)
        self.contextMenu.addAction(self.createFolderAction)
        self.createFolderAction.triggered.connect(self.slot_createFolder)
        
        self.contextMenu.addSeparator()
        
        self.addNewFileAction = QAction(QIcon("icons/project_management/add_new_file.png"), "Add new file", self)
        self.contextMenu.addAction(self.addNewFileAction)
        self.addNewFileAction.triggered.connect(self.slot_addNewFile)
        
        self.addExistingFileAction = QAction(QIcon("icons/project_management/add_existing_file.png"), "Add existing file(s)", self)
        self.contextMenu.addAction(self.addExistingFileAction)
        self.addExistingFileAction.triggered.connect(self.slot_addExistingFile)
        
        self.contextMenu.addSeparator()
        
        self.renameAction = QAction(QIcon("icons/project_management/rename.png"), "Rename file/folder", self)
        self.contextMenu.addAction(self.renameAction)
        self.renameAction.triggered.connect(self.slot_renameAction)
        
        self.removeAction = QAction(QIcon("icons/project_management/remove.png"), "Remove file(s)/folder(s)", self)
        self.contextMenu.addAction(self.removeAction)
        self.removeAction.triggered.connect(self.slot_removeAction)
        
        self.view.customContextMenuRequested.connect(self.slot_customContextMenu)
        
    def setProject(self, project):
        self.setEnabled(project is not None)
        
        self.view.setModel(project)
    
    @staticmethod    
    def getItemFromModelIndex(modelIndex):
        # todo: is this ugly thing really the way to do this?
        
        # Qt says in the docs that returned parent is never None but can be invalid if it's the root
        if not modelIndex.parent().isValid():
            # if it's invalid, we can use the indices as absolute model top level indices
            return modelIndex.model().item(modelIndex.row(), modelIndex.column())
        else:
            # otherwise, resort to recursion
            return ProjectManager.getItemFromModelIndex(modelIndex.parent()).child(modelIndex.row(), modelIndex.column())
        
    def slot_itemDoubleClicked(self, modelIndex):
        if not modelIndex.model():
            return

        item = ProjectManager.getItemFromModelIndex(modelIndex)
        if item.itemType == Item.File: # only react to files, expanding folders is handled by Qt
            self.fileOpenRequested.emit(item.getAbsolutePath())
            
    def slot_customContextMenu(self, point):
        if self.isEnabled():
            # Qt fails at English a bit?
            selectedIndices = self.view.selectedIndexes()
            # </grammar-nazi-mode>
            
            # we set everything to disabled and then enable what's relevant
            self.createFolderAction.setEnabled(False)
            self.addNewFileAction.setEnabled(False)
            self.addExistingFileAction.setEnabled(False)
            self.renameAction.setEnabled(False)
            self.removeAction.setEnabled(False)
            
            if len(selectedIndices) == 0:
                # create root folder
                self.createFolderAction.setEnabled(True)
                self.addNewFileAction.setEnabled(True)
                self.addExistingFileAction.setEnabled(True)
            
            elif len(selectedIndices) == 1:
                index = selectedIndices[0]
                item = self.getItemFromModelIndex(index)
                
                if item.itemType == Item.Folder:
                    # create folder inside folder
                    self.createFolderAction.setEnabled(True)
                    self.addNewFileAction.setEnabled(True)
                    self.addExistingFileAction.setEnabled(True)
                
                self.renameAction.setEnabled(True)    
                self.removeAction.setEnabled(True)
            
            else:
                # more than 1 selected item
                self.removeAction.setEnabled(True)
            
                #for index in selectedIndices:
                #    item = self.getItemFromModelIndex(index)
        
        self.contextMenu.exec_(self.mapToGlobal(point))
    
    def slot_createFolder(self):
        ## TODO: Name clashes!
        
        text, ok = QInputDialog.getText(self,
                                        "Create a folder (only affects project file)",
                                        "Name",
                                        QLineEdit.Normal,
                                        "New folder")
        
        if ok:
            item = Item(self.project)
            item.itemType = Item.Folder
            item.name = text
                
            selectedIndices = self.view.selectedIndexes()
            
            if len(selectedIndices) == 0:
                self.project.appendRow(item)
                
            else:
                assert(len(selectedIndices) == 1)
                
                parent = self.getItemFromModelIndex(selectedIndices[0])
                assert(parent.itemType == Item.Folder)
                
                parent.appendRow(item)
    
    def slot_addNewFile(self):
        ## TODO: name clashes, duplicates
        
        file, filter = QFileDialog.getSaveFileName(
                        self,
                        "Create a new file and add it to the project",
                        self.project.getAbsolutePathOf(""))
        
        try:
            f = open(file, "w")
            f.close()
            
        except OSError:
            QMessageBox.question(self,
                                 "Can't create file!",
                                 "Creating file '%s' failed. Exception details follow: %s" % (file, sys.exc_info()[0]),
                                 QMessageBox.Ok)
            
            return
        
        selectedIndices = self.view.selectedIndexes()
        
        item = Item(self.project)
        item.itemType = Item.File
        item.path = self.project.getRelativePathOf(file)
        
        if len(selectedIndices) == 0:
            self.project.appendRow(item)
               
        else:
            assert(len(selectedIndices) == 1)
            
            parent = self.getItemFromModelIndex(selectedIndices[0])
            assert(parent.itemType == Item.Folder)
            
            parent.appendRow(item)
    
    def slot_addExistingFile(self):
        ## TODO: name clashes, duplicates
        
        files, filter = QFileDialog.getOpenFileNames(
                        self,
                        "Select one or more files to add to the project",
                        self.project.getAbsolutePathOf(""))
        selectedIndices = self.view.selectedIndexes()
        
        for file in files:
            item = Item(self.project)
            item.itemType = Item.File
            item.path = self.project.getRelativePathOf(file)
            
            if len(selectedIndices) == 0:
                self.project.appendRow(item)
                   
            else:
                assert(len(selectedIndices) == 1)
                
                parent = self.getItemFromModelIndex(selectedIndices[0])
                assert(parent.itemType == Item.Folder)
                
                parent.appendRow(item)
             
    def slot_renameAction(self):
        ## TODO: Name clashes!
        
        selectedIndices = self.view.selectedIndexes()
        assert(len(selectedIndices) == 1)
        
        item = self.getItemFromModelIndex(selectedIndices[0])
        if item.itemType == Item.File:
            text, ok = QInputDialog.getText(self,
                                        "Rename file (renames the file on the disk!)",
                                        "New name",
                                        QLineEdit.Normal,
                                        os.path.basename(item.path))
            
            if ok and text != os.path.basename(item.path):
                # legit change
                newPath = os.path.join(os.path.dirname(item.path), text)
                
                try:
                    os.rename(self.project.getAbsolutePathOf(item.path), self.project.getAbsolutePathOf(newPath))
                    item.path = newPath
                    
                except OSError:
                    QMessageBox.question(self,
                                      "Can't rename!",
                                      "Renaming file '%s' to '%s' failed. Exception details follow: %s" % (item.path, newPath, sys.exc_info()[0]),
                                      QMessageBox.Ok)
        
        elif item.itemType == Item.Folder:
            text, ok = QInputDialog.getText(self,
                                        "Rename folder (only affects the project file)",
                                        "New name",
                                        QLineEdit.Normal,
                                        item.name)
            
            if ok and text != item.name:
                item.name = text
            
    def slot_removeAction(self):
        if not self.isEnabled():
            return
        
        selectedIndices = self.view.selectedIndexes()
        
        removeSpec = ""
        if len(selectedIndices) == 1:
            item = self.getItemFromModelIndex(selectedIndices[0])
            removeSpec = "'%s'" % (item.label)
        else:
            removeSpec = "%i project items" % (len(selectedIndices))
        
        # we have changes, lets ask the user whether we should dump them or save them
        result = QMessageBox.question(self,
                                      "Remove items?",
                                      "Are you sure you want to remove %s from the project? "
                                      "This action can't be undone! "
                                      "(Pressing Cancel will cancel the operation!)" % (removeSpec),
                                      QMessageBox.Yes | QMessageBox.Cancel,
                                      QMessageBox.Cancel)
        
        if result == QMessageBox.Cancel:
            # user chickened out ;-)
            return
            
        elif result == QMessageBox.Yes:
            selectedIndices = sorted(selectedIndices, key = lambda index: index.row(), reverse = True)
            removeCount = 0
            
            # we have to remove files first because multi-selection could screw us otherwise
            # (Parent also removes it's children)
            
            # first remove files
            for index in selectedIndices:
                item = self.getItemFromModelIndex(index)
                
                if not item:
                    continue
                
                if (item.itemType == Item.File):
                    index.model().removeRow(index.row(), index.parent())
                    removeCount += 1
            
            # then remove folders
            for index in selectedIndices:
                item = self.getItemFromModelIndex(index)
                
                if not item:
                    continue
                
                if (item.itemType == Item.Folder):
                    index.model().removeRow(index.row(), index.parent())
                    removeCount += 1
            
            if len(selectedIndices) - removeCount > 0:        
                print "%i selected project items are unknown and can't be deleted" % (len(selectedIndices))
        
class NewProjectDialog(QDialog):
    def __init__(self):
        super(NewProjectDialog, self).__init__()
        
        self.ui = ui.newprojectdialog.Ui_NewProjectDialog()
        self.ui.setupUi(self)
        
        self.projectName = self.findChild(QLineEdit, "projectName")
        
        self.projectFilePath = self.findChild(qtwidgets.FileLineEdit, "projectFilePath")
        self.projectFilePath.filter = "Project file (*.project)"
        self.projectFilePath.mode = qtwidgets.FileLineEdit.NewFileMode    
    
    # creates the project using data from this dialog    
    def createProject(self):
        ret = Project()
        ret.name = self.projectName.text()
        ret.projectFilePath = self.projectFilePath.text()
        
        return ret

class ProjectSettingsDialog(QDialog):
    def __init__(self, project):
        super(ProjectSettingsDialog, self).__init__()
        
        self.ui = ui.projectsettingsdialog.Ui_ProjectSettingsDialog()
        self.ui.setupUi(self)
        
        self.projectName = self.findChild(QLineEdit, "projectName")
        self.baseDirectory = self.findChild(qtwidgets.FileLineEdit, "baseDirectory")
        self.baseDirectory.mode = qtwidgets.FileLineEdit.ExistingDirectoryMode
    
        self.resourceDirectory = self.findChild(qtwidgets.FileLineEdit, "resourceDirectory")
        self.resourceDirectory.mode = qtwidgets.FileLineEdit.ExistingDirectoryMode
        self.resourceDirectoryApplyButton = self.findChild(QPushButton, "resourceDirectoryApplyButton")
        self.resourceDirectoryApplyButton.pressed.connect(self.slot_applyResourceDirectory)
    
        self.imagesetsPath = self.findChild(qtwidgets.FileLineEdit, "imagesetsPath")
        self.imagesetsPath.mode = qtwidgets.FileLineEdit.ExistingDirectoryMode
        self.fontsPath = self.findChild(qtwidgets.FileLineEdit, "fontsPath")
        self.fontsPath.mode = qtwidgets.FileLineEdit.ExistingDirectoryMode
        self.looknfeelsPath = self.findChild(qtwidgets.FileLineEdit, "looknfeelsPath")
        self.looknfeelsPath.mode = qtwidgets.FileLineEdit.ExistingDirectoryMode
        self.schemesPath = self.findChild(qtwidgets.FileLineEdit, "schemesPath")
        self.schemesPath.mode = qtwidgets.FileLineEdit.ExistingDirectoryMode
        self.layoutsPath = self.findChild(qtwidgets.FileLineEdit, "layoutsPath")
        self.layoutsPath.mode = qtwidgets.FileLineEdit.ExistingDirectoryMode
        
        self.projectName.setText(project.name)
        self.baseDirectory.setText(project.getAbsolutePathOf(""))
        self.imagesetsPath.setText(project.getAbsolutePathOf(project.imagesetsPath))
        self.fontsPath.setText(project.getAbsolutePathOf(project.fontsPath))
        self.looknfeelsPath.setText(project.getAbsolutePathOf(project.looknfeelsPath))
        self.schemesPath.setText(project.getAbsolutePathOf(project.schemesPath))
        self.layoutsPath.setText(project.getAbsolutePathOf(project.layoutsPath))
        
    def apply(self, project):
        project.name = self.projectName.text()
        absBaseDir = os.path.normpath(os.path.abspath(self.baseDirectory.text()))
        project.baseDirectory = os.path.relpath(absBaseDir, os.path.dirname(project.projectFilePath))
        
        project.imagesetsPath = os.path.relpath(self.imagesetsPath.text(), absBaseDir)
        project.fontsPath = os.path.relpath(self.fontsPath.text(), absBaseDir)
        project.looknfeelsPath = os.path.relpath(self.looknfeelsPath.text(), absBaseDir)
        project.schemesPath = os.path.relpath(self.schemesPath.text(), absBaseDir)
        project.layoutsPath = os.path.relpath(self.layoutsPath.text(), absBaseDir)
        
    def slot_applyResourceDirectory(self):
        resourceDir = os.path.normpath(os.path.abspath(self.resourceDirectory.text()))
        
        self.imagesetsPath.setText(os.path.join(resourceDir, "imagesets"))
        self.fontsPath.setText(os.path.join(resourceDir, "fonts"))
        self.looknfeelsPath.setText(os.path.join(resourceDir, "looknfeel"))
        self.schemesPath.setText(os.path.join(resourceDir, "schemes"))
        self.layoutsPath.setText(os.path.join(resourceDir, "layouts"))
        