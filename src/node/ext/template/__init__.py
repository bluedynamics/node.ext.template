from node.ext import directory
from node.ext.directory import File
from node.ext.template._api import (
    SectionedTemplate,
    DTMLTemplate,
    JinjaTemplate,
    XMLTemplate,
    ZPTemplate,
)

#directory.file_factories['.rst'] = JinjaTemplate
#directory.file_factories['.xml'] = XMLTemplate
#directory.file_factories['.pt'] = ZPTemplate
# XXX
directory.file_factories['.rst'] = File
directory.file_factories['.pt'] = File