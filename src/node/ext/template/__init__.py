from node.ext.template.template import (
    SectionedTemplate,
    DTMLTemplate,
    JinjaTemplate,
    XMLTemplate,
    ZPTemplate,
)
from node.ext import directory


directory.file_factories['.rst'] = JinjaTemplate
directory.file_factories['.xml'] = XMLTemplate
directory.file_factories['.pt'] = ZPTemplate
