Code Section Handler
====================

The code section handler is responsible for managing protected code of some
existing target file.

Create some mock code lines, as expected by the code section handler::

    >>> codelines = [
    ...     'first line',
    ...     '##code-section foo',
    ...     'section foo',
    ...     '##/code-section foo',
    ...     'in between',
    ...     '##code-section bar',
    ...     'section bar',
    ...     '##/code-section bar',
    ...     'last line',
    ... ]

Create code section handler instance::

    >>> from node.ext.template.codesectionhandler import CodeSectionHandler
    >>> handler = CodeSectionHandler(codelines)
    >>> handler
    <node.ext.template.codesectionhandler.CodeSectionHandler object at ...>
  
Read section names::

    >>> names = handler.sectionnames
    >>> names.sort()
    >>> names
    ['bar', 'foo']

Read section contents::

    >>> handler.getsection('foo')
    ['section foo']
  
Set the contents for a code section::

    >>> handler.setsection('foo', ['set contents for foo'])
    >>> handler.getsection('foo')
    ['set contents for foo']

Note that patterns of code sections might differ by usecase. The protected
section indication is controlled by the attributes ``SECTION_BEGIN`` and
``SECTION_END``::

    >>> handler.SECTION_BEGIN
    '##code-section'
  
    >>> handler.SECTION_END
    '##/code-section'

The handler then uses patterns to detect the sections::
  
    >>> handler.BEGIN_PATTERN
    '##code-section %s'
  
    >>> handler.END_PATTERN
    '##/code-section %s'

If you want to mark protected sections i.e. in XML comment style you have to
set ``SECTION_POSTFIX``, which is then appended to ``BEGIN_PATTERN`` and
``END_PATTERN``::

    >>> handler.SECTION_BEGIN = '<!-- code-section'
    >>> handler.SECTION_END = '<!-- /code-section'
    >>> handler.SECTION_POSTFIX = ' -->'
  
    >>> handler.BEGIN_PATTERN
    '<!-- code-section %s -->'
  
    >>> handler.END_PATTERN
    '<!-- /code-section %s -->'
  
Check if code with other section indication works as well::

    >>> codelines = [
    ...     '<!-- code-section 1 -->' ,
    ...     '<foo />',
    ...     '<!-- /code-section 1 -->',
    ...     '<!-- code-section 2 -->' ,
    ...     '<bar />',
    ...     '<!-- /code-section 2 -->' ,
    ... ]
  
    >>> handler.codelines = codelines
    >>> handler.sectionnames
    ['1', '2']
  
    >>> handler.getsection('1')
    ['<foo />']
  
    >>> handler.setsection('1', ['<nofoo>'])
    >>> handler.getsection('1')
    ['<nofoo>']
