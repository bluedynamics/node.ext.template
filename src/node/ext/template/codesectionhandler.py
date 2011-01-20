class CodeSectionHandler(object):
    """Class CodeSectionHandler is responsible to get and set code sections
    inside some kind of code buffer.

    A code section starts with ``self.BEGIN_PATTERN % sectionname``
    and ends with ``self.END_PATTERN % sectionname``...

    ..., where ``self.BEGIN_PATTERN`` defines a protected section and the
    following string, the example ``sectionname`` is the identifier or name of
    the section, since we want to be able to define several protected sections.

    You can control begin and end patterns due ``self.SECTION_BEGIN`` and
    ``self.SECTION_END`` attributes.
    """

    # XXX: improve code section handler to be able to use section patterns
    #      which can contain characters after section name.

    SECTION_BEGIN = '##code-section'
    SECTION_END = '##/code-section'
    SECTION_POSTFIX = ''

    @property
    def BEGIN_PATTERN(self):
        return self.SECTION_BEGIN + ' %s' + self.SECTION_POSTFIX

    @property
    def END_PATTERN(self):
        return self.SECTION_END + ' %s' + self.SECTION_POSTFIX

    def __init__(self, lines):
        """Create code section handler.

        @param lines: list of code lines.
        """
        self.codelines = lines

    @property
    def sectionnames(self):
        """List of existent section names in code buffer.
        """
        names = list()
        section = False
        for line in self.codelines:
            if line.find(self.SECTION_BEGIN) != -1:
                if section:
                    raise ValueError(u"Section end pattern not set.")
                section = True
                idx = line.find(self.SECTION_BEGIN) + len(self.SECTION_BEGIN)
                if self.SECTION_POSTFIX:
                    name = line[idx:].strip()
                    name = name[:name.find(self.SECTION_POSTFIX)].strip()
                else:
                    name = line[idx:].strip()
                names.append(name)
            if section and line.find(self.END_PATTERN % names[-1]) != -1:
                section = False
        if section:
            raise ValueError(u"Section end pattern not set.")
        return names

    def getsection(self, name):
        """Return contents of the code section by name.

        @param name: name of the section
        """
        ret = []
        sectioncontent = False
        for line in self.codelines:
            if line.find(self.END_PATTERN % name) != -1:
                return ret
            if sectioncontent:
                ret.append(line)
            if line.find(self.BEGIN_PATTERN % name) != -1:
                sectioncontent = True
        raise Exception(
            '%s - Section not found or no section end pattern set.'
            % name)

    def setsection(self, name, code):
        """Set the contents of code section by name.

        @param name: name of the section
        @param code: list of codelines
        """
        index = 0
        startindex = None
        for line in self.codelines:
            if line.find(self.END_PATTERN % name) != -1:
                if startindex is None:
                    raise Exception('Section start not found')
                cl = self.codelines
                self.codelines = cl[0:startindex + 1] + code + cl[index:]
                return
            if line.find(self.BEGIN_PATTERN % name) != -1:
                startindex = index
            index += 1
        raise Exception(
            '%s - Section not found or no section end pattern set.'
            % name)
