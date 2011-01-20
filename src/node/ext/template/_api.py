import codecs
import os
from StringIO import StringIO
from zope.interface import implements
from zodict.node import Node
from agx.io.template.interfaces import ITemplate
from zope.documenttemplate import HTML
from jinja2 import Template as JTemplate
from chameleon.zpt.template import PageTemplate
from codesectionhandler import CodeSectionHandler

class TemplateBase(Node):
    """Base template.
    """

    implements(ITemplate)

    def __init__(self, path=None):
        """Initialize template.

        @param path: path to output target
        """
        Node.__init__(self, name=path)
        self.params = dict()
        self.template = None

    def __call__(self):
        raise NotImplementedError(u"Abstract template handler does not "
                                   "implement ``__call__()``")

    __repr__ = object.__repr__

    def existentbuffer(self, target):
        """Try to read target file and return its contents as list of lines.

        @param target: target file path
        """
        try:
            existentfile = codecs.open(os.path.join(target),
                                       'r', encoding='utf-8')
            existentbuffer = existentfile.readlines()
            existentfile.close()
        except IOError:
            existentbuffer = []
        return existentbuffer

    def write(self, buffer):
        """Write buffer to target.
        """
        outfile = codecs.open(self.abspath, 'w', encoding='utf-8')
        outfile.writelines(buffer)
        outfile.close()

    @property
    def abspath(self):
        return os.path.join(*self.path)

class SectionedTemplate(TemplateBase, CodeSectionHandler):
    """Template implementation providing to handle code sections.
    """

    def __call__(self):
        self.write(self.handlesections(self.existentbuffer(self.abspath),
                                       self.existentbuffer(self.template)))

    def handlesections(self, existent, generated):
        """Read code sections from existent buffer and fill those one found
        in generated buffer.
        """
        sections = dict()
        CodeSectionHandler.__init__(self, existent)
        for name in self.sectionnames:
            sections[name] = self.getsection(name)
        CodeSectionHandler.__init__(self, generated)
        for name in self.sectionnames:
            if name in sections.keys():
                self.setsection(name, sections[name])
        return self.codelines

class JinjaTemplate(SectionedTemplate):
    """Template handler using ``jinja2.Template`` templates for
    output generation.
    """

    def __call__(self):
        self.write(self.handlesections(self.existentbuffer(self.abspath),
                                       self.execjinja()))

    def execjinja(self):
        params = self.params.copy()
        params.update(__builtins__)
        templatefile = open(self.template)
        template = templatefile.read()
        templatefile.close()
        template = JTemplate(template)
        return [line + u"\n"
            for line in template.render(**params).split(u"\n")]

class DTMLTemplate(SectionedTemplate):
    """Template handler using ``zope.documenttemplate.HTML`` templates for
    output generation.
    """

    def __call__(self):
        self.write(self.handlesections(self.existentbuffer(self.abspath),
                                       self.execdtml()))

    def execdtml(self):
        """Call self.template as DTML template with self.params as
        arguments and return generated code as list of lines.
        """
        params = self.params.copy()
        params.update(__builtins__)
        templatefile = open(self.template)
        template = templatefile.read()
        templatefile.close()
        template = HTML(template, params)
        try:
            template = template()
            return StringIO(template).readlines()
        except Exception:
            msg = "Problem rendering %s\n" % self.template
            msg += "params = %s" % self.params
            print msg
            raise

class XMLTemplate(DTMLTemplate):
    """Template handler for XML files.
    """

    SECTION_BEGIN = '<!-- code-section'
    SECTION_END = '<!-- /code-section'
    SECTION_POSTFIX = ' -->'

class ZPTemplate(PageTemplate):
    """ Template handler for zope page templates
    """
