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

from ceed import compatibility
from xml.etree import ElementTree

CEGUILayout2 = "CEGUI layout 2"
CEGUILayout3 = "CEGUI layout 3"
CEGUILayout4 = "CEGUI layout 4"

class Layout2TypeDetector(compatibility.TypeDetector):
    def getType(self):
        return CEGUILayout2
    
    def getPossibleExtensions(self):
        return ["layout"]
    
    def matches(self, data, extension):
        if extension not in ["", "layout"]:
            return False
        
        # todo: we should be at least a bit more precise
        # (implement XSD based TypeDetector?)
        
        try:
            root = ElementTree.fromstring(data)
            if root.tag != "GUILayout":
                return False
            
            # Layout 2 has no version indication :-(
            # However if there is a version attribute, we can be sure it's not Layout2
            if root.get("version") is not None:
                return False
            
            return True
        
        except:
            return False

class Layout3TypeDetector(compatibility.TypeDetector):
    def getType(self):
        return CEGUILayout3
    
    def getPossibleExtensions(self):
        return ["layout"]
    
    def matches(self, data, extension):
        if extension not in ["", "layout"]:
            return False
        
        # todo: we should be at least a bit more precise
        # (implement XSD based TypeDetector?)
        
        try:
            root = ElementTree.fromstring(data)
            if root.tag != "GUILayout":
                return False
            
            # Layout 3 has no version indication :-(
            # However if there is a version attribute, we can be sure it's not Layout3
            if root.get("version") is not None:
                return False
            
            return True
        
        except:
            return False

class Layout4TypeDetector(compatibility.TypeDetector):
    def getType(self):
        return CEGUILayout4
    
    def getPossibleExtensions(self):
        return ["layout"]
    
    def matches(self, data, extension):
        if extension not in ["", "layout"]:
            return False
        
        # todo: we should be at least a bit more precise
        # (implement XSD based TypeDetector?)
        
        try:
            root = ElementTree.fromstring(data)
            if root.tag != "GUILayout":
                return False
            
            if root.get("version", "unknown") != "4":
                return False
            
            return True
        
        except:
            return False
        
class Layout3To4Layer(compatibility.Layer):
    def getSourceType(self):
        return CEGUILayout3
    
    def getTargetType(self):
        return CEGUILayout4
    
    def convertToRelativeNames(self, window, leadingName = ""):
        ret = ""
        
        name = window.get("Name", "")
    
        if name.startswith(leadingName + "/"):
            name = name[len(leadingName + "/"):]
            
            for childWindow in window.findall("Window"):
                ret += self.convertToRelativeNames(childWindow, leadingName + "/" + name)
        else:
            
            for childWindow in window.findall("Window"):
                ret += self.convertToRelativeNames(childWindow, name)
        
        delimiterPosition = name.rfind("/")        
        if delimiterPosition != -1:
            oldName = name
            name = name[delimiterPosition + 1:]
            
            ret += "Warning: Renaming '%s' to '%s' because it contains '/' even after prefix stripping (and '/' is a disallowed character!)\n" % (oldName, name)
    
        window.set("Name", name)
        
        return ret
    
    def convertAutoWindowSuffix(self, autoWindow):
        autoWindow.set("NamePath", autoWindow.get("NameSuffix"))
        del autoWindow.attrib["NameSuffix"]
    
        for childAutoWindow in autoWindow.findall("AutoWindow"):
            self.convertAutoWindowSuffix(childAutoWindow)
    
    @classmethod
    def transformPropertiesOf(cls, element, tag = "Property", nameAttribute = "Name", valueAttribute = "Value"):
        windowType = element.get("Type")

        # convert the properties that had 'Unified' prefix
        for property in element.findall(tag):
            name = property.get(nameAttribute, "")
            
            if name == "UnifiedAreaRect":
                name = "Area"
            elif name == "UnifiedPosition":
                name = "Position"
            elif name == "UnifiedXPosition":
                name = "XPosition"
            elif name == "UnifiedYPosition":
                name = "YPosition"
            elif name == "UnifiedSize":
                name = "Size"
            elif name == "UnifiedWidth":
                name = "Width"
            elif name == "UnifiedHeight":
                name = "Height"
            elif name == "UnifiedMinSize":
                name = "MinSize"
            elif name == "UnifiedMaxSize":
                name = "MaxSize"
            
            if name != "":
                property.set(nameAttribute, name)
        
            def convertImagePropertyToName(property):
                value = property.get(valueAttribute)
                split = value.split("image:", 1)
                assert(len(split) == 2)
                split[0] = split[0][4:] # get rid of "set:"
                
                # strip both of whitespaces left and right
                split[0] = split[0].strip()
                split[1] = split[1].strip()
                
                property.set(valueAttribute, "%s/%s" % (split[0], split[1]))
        
            if windowType is None or windowType.endswith("StaticImage"):
                if name == "Image":
                    convertImagePropertyToName(property)
                    
            elif windowType is None or windowType.endswith("ImageButton"):
                if name in ["NormalImage", "HoverImage", "PushedImage"]:
                    convertImagePropertyToName(property)
    
    def applyChangesRecursively(self, window):
        ret = ""
        
        Layout3To4Layer.transformPropertiesOf(window)
        
        # convert NameSuffix to NamePath
        for autoWindow in window.findall("AutoWindow"):
            self.convertAutoWindowSuffix(autoWindow)
        
        for childWindow in window.findall("Window"):
            self.applyChangesRecursively(childWindow)
            
        #window.tag = "Widget"
        
        return ret
    
    def transform(self, data):
        log = ""
        
        root = ElementTree.fromstring(data)
        
        # version 4 has a version attribute
        root.set("version", "4")
        
        for window in root.findall("Window"):
            # should be only one window
            
            # first make the names relative to parent
            log += self.convertToRelativeNames(window)
            
            # apply other changes
            log += self.applyChangesRecursively(window)
            
        return ElementTree.tostring(root, "utf-8")

class Layout4To3Layer(compatibility.Layer):
    def getSourceType(self):
        return CEGUILayout4
    
    def getTargetType(self):
        return CEGUILayout3
    
    def convertToAbsoluteNames(self, window, leadingName = ""):
        ret = ""
        
        name = window.get("Name", "")
        if leadingName != "":
            name = leadingName + "/" + name
        
        for childWindow in window.findall("Window"):
            ret += self.convertToAbsoluteNames(childWindow, name)
    
        window.set("Name", name)
        
        return ret
    
    def convertAutoWindowSuffix(self, autoWindow):
        autoWindow.set("NameSuffix", autoWindow.get("NamePath"))
        del autoWindow.attrib["NamePath"]
    
        for childAutoWindow in autoWindow.findall("AutoWindow"):
            self.convertAutoWindowSuffix(childAutoWindow)
    
    @classmethod
    def transformPropertiesOf(cls, element, tag = "Property", nameAttribute = "Name", valueAttribute = "Value"):
        windowType = element.get("Type")
        
        # convert the properties that had 'Unified' prefix in 0.7
        for property in element.findall(tag):
            name = property.get(nameAttribute, "")
            
            if name == "Area":
                name = "UnifiedAreaRect"
            elif name == "Position":
                name = "UnifiedPosition"
            elif name == "XPosition":
                name = "UnifiedXPosition"
            elif name == "YPosition":
                name = "UnifiedYPosition"
            elif name == "Size":
                name = "UnifiedSize"
            elif name == "Width":
                name = "UnifiedWidth"
            elif name == "Height":
                name = "UnifiedHeight"
            elif name == "MinSize":
                name = "UnifiedMinSize"
            elif name == "MaxSize":
                name = "UnifiedMaxSize"
            
            if name != "":
                property.set(nameAttribute, name)
                
            def convertImagePropertyToImagesetImage(property):
                value = property.get(valueAttribute)
                split = value.split("/", 1)
                assert(len(split) == 2)
                property.set(valueAttribute, "set:%s image:%s" % (split[0], split[1]))
        
            if windowType is None or windowType.endswith("StaticImage"):
                if name == "Image":
                    convertImagePropertyToImagesetImage(property)
                    
            elif windowType is None or windowType.endswith("ImageButton"):
                if name in ["NormalImage", "HoverImage", "PushedImage"]:
                    convertImagePropertyToImagesetImage(property)
    
    def applyChangesRecursively(self, window):
        ret = ""
        
        Layout4To3Layer.transformPropertiesOf(window)
                
        # convert NameSuffix to NamePath
        for autoWindow in window.findall("AutoWindow"):
            self.convertAutoWindowSuffix(autoWindow)
        
        for childWindow in window.findall("Window"):
            self.applyChangesRecursively(childWindow)

        return ret
    
    def transform(self, data):
        log = ""
        
        root = ElementTree.fromstring(data)
        
        # version 3 must not have a version attribute
        del root.attrib["version"]
        
        for window in root.findall("Window"):
            # should be only one window
            
            # first make the names relative to parent
            log += self.convertToAbsoluteNames(window)
            
            # apply other changes
            log += self.applyChangesRecursively(window)
            
        return ElementTree.tostring(root, "utf-8")