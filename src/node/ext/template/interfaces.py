# Copyright BlueDynamics Alliance - http://bluedynamics.com
# GNU General Public License Version 2

from zope.interface import Attribute
from agx.io.directory import IFile

class ITemplate(IFile):
    """A template.
    """
    template = Attribute(u"Template source path")