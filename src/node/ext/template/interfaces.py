from zope.interface import Attribute
from node.ext.directory import IFile

class ITemplate(IFile):
    """A template.
    """
    template = Attribute(u"Template source path")
