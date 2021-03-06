Template
========

``node.ext.template.interfaces.ITemplate`` implementations are
responsible to create and dump concrete generated files to the filesystem.

At ``__init__`` time, this objects expect a template path.

Set up a Test environment. Create a temporary directory::

    >>> import codecs
    >>> import os
    >>> import tempfile
    >>> tempdir = tempfile.mkdtemp()


Abstract base template
----------------------

There exists an abstract template implementation. It provides some
convenience::

    >>> from node.ext.template.template import TemplateBase
    >>> targetpath = os.path.join(tempdir, 'abstractbase.txt')
    >>> targetpath
    '...abstractbase.txt'

    >>> abstracttemplate = TemplateBase(targetpath)
    >>> abstracttemplate
    <node.ext.template.template.TemplateBase object at ...>

    >>> abstracttemplate.path
    ['...abstractbase.txt']

The internal representation of files or parts of a file is always a list of
lines, we call it buffers.

There is no existing buffer yet for targetpath::

    >>> abstracttemplate.existentbuffer(targetpath)
    []

Write some buffer to target file::

    >>> abstracttemplate.write([u'foo\n', u'bar\n', u'baz\n'])
    >>> os.path.exists(targetpath)
    True

And check the existentbuffer again::

    >>> abstracttemplate.existentbuffer(targetpath)
    [u'foo\n', u'bar\n', u'baz\n']

The template has an attribute params, which is the dict to put template
generation specific data::
 
    >>> abstracttemplate.params
    {}
    >>> abstracttemplate.params['foo'] = 'foo'
    >>> abstracttemplate.params['bar'] = object()
    >>> keys = abstracttemplate.params.keys()
    >>> sorted(keys)
    ['bar', 'foo']

By interface the ``__call__`` function is responsible for writing. Since our
base template is abstract this will fail::

    >>> abstracttemplate()
    Traceback (most recent call last):
      ...
    NotImplementedError: Abstract template handler does not implement 
    ``__call__()``


Template for files containing protected sections
------------------------------------------------

Another common technique in generated code is the use of protected code
sections. This are parts of a generated file which content never get touched.
A protected section has always a name and begins and ends with a string pattern.
See ``codesectionhandler.txt`` for more details.

The template for protected sections provides convenience to hook the
contents of protected sections of already existing files back to some output
buffer before overwriting files. On ``__call__ `` this is done transparent.

Create some test environment. We need a template containing a protected
section::

    >>> sectionedtemplate = u"""
    ... ##code-section first
    ... ##/code-section first
    ... 
    ... slightly modified generated stuff
    ... """
    >>> sectionedtemplatetarget = os.path.join(tempdir,
    ...                                        'sectionedtemplate.txt')
    >>> with codecs.open(sectionedtemplatetarget, 'w', encoding='utf-8') as out:
    ...    out.write(sectionedtemplate)

And some generated and modified file::

    >>> manuallymodified = u"""
    ... ##code-section first
    ... i am the manually created content
    ... ##/code-section first
    ... 
    ... generated stuff
    ... """
    >>> manuallymodifiedtarget = os.path.join(tempdir,
    ...                                       'manuallymodified.txt')
    >>> with codecs.open(manuallymodifiedtarget, 'w', encoding='utf-8') as out:
    ...     out.write(manuallymodified)

Now create the template::

    >>> from node.ext.template import SectionedTemplate
    >>> sectiontemplate = SectionedTemplate(manuallymodifiedtarget)
    >>> sectiontemplate.template = sectionedtemplatetarget
    >>> sectiontemplate
    <node.ext.template.template.SectionedTemplate object at ...>

First check expected functionality manually::

    >>> out = sectiontemplate.existentbuffer(sectionedtemplatetarget)
    >>> out
    [u'\n', u'##code-section first\n', u'##/code-section first\n', 
    u'\n', u'slightly modified generated stuff\n']

    >>> existent = sectiontemplate.existentbuffer(manuallymodifiedtarget)
    >>> existent
    [u'\n', u'##code-section first\n', u'i am the manually created content\n', 
    u'##/code-section first\n', u'\n', u'generated stuff\n']

The ``handlesections`` function reads the protected section from existent buffer
and writes its contents to the refering protected section in output buffer if
it exists::

    >>> sectiontemplate.handlesections(existent, out)
    [u'\n', u'##code-section first\n', u'i am the manually created content\n', 
    u'##/code-section first\n', u'\n', u'slightly modified generated stuff\n']

If there is no existent buffer, there's nothing to hook::

    >>> sectiontemplate.handlesections([], out)
    [u'\n', u'##code-section first\n', u'##/code-section first\n', 
    u'\n', u'slightly modified generated stuff\n']

``__call__`` does all that for you and overwrites the target::

    >>> sectiontemplate()
    >>> with codecs.open(manuallymodifiedtarget, 'r', encoding='utf-8') as over:
    ...     over.readlines()
    [u'\n', 
    u'##code-section first\n', 
    u'i am the manually created content\n', 
    u'##/code-section first\n', u'\n', 
    u'slightly modified generated stuff\n']


DTML templates
--------------

Most of the time you need a little bit more than protected section handling
when building generation templates, such as parameters for dynamic generation.

The DTML template provides this by handling ``self.template`` as path
to a DTML template and passes the ``params`` dict of self to the template call.
Protected sections are still handled.

Create some test environment. We need a DTML template::

    >>> dtmltemplate = u"""
    ... ##code-section first
    ... ##/code-section first
    ... 
    ... Param modified: <dtml-var "someparam">
    ... """
    >>> dtmltemplatetarget = os.path.join(tempdir,
    ...                                   'dtmltemplate.txt')
    >>> with codecs.open(dtmltemplatetarget, 'w', encoding='utf-8') as out:
    ...     out.write(dtmltemplate)

And an existing by this template generated file::

    >>> dtmlmodified = u"""
    ... ##code-section first
    ... i am the manually created content
    ... ##/code-section first
    ... 
    ... Param modified: Somevalue
    ... """
    >>> dtmlmodifiedtarget = os.path.join(tempdir,
    ...                                   'dtmlmodified.txt')
    >>> with codecs.open(dtmlmodifiedtarget, 'w', encoding='utf-8') as out:
    ...     out.write(dtmlmodified)

Create the DTML template::

    >>> from node.ext.template import DTMLTemplate
    >>> dtmltemplate = DTMLTemplate(dtmlmodifiedtarget)
    >>> dtmltemplate.template = dtmltemplatetarget
    >>> dtmltemplate
    <node.ext.template.template.DTMLTemplate object at ...>

Check the DTML execution::

    >>> dtmltemplate.params['someparam'] = u'Anothervalue'
    >>> dtmltemplate.execdtml()
    [u'\n', 
    u'##code-section first\n', 
    u'##/code-section first\n', 
    u'\n', 
    u'Param modified: Anothervalue\n']

Lets do the handler's ``__call__`` the work::

    >>> dtmltemplate.params['someparam'] = u'FooBarBaz'
    >>> dtmltemplate()
    >>> with codecs.open(dtmlmodifiedtarget, 'r', encoding='utf-8') as over:
    ...     over.readlines()
    [u'\n', 
    u'##code-section first\n', 
    u'i am the manually created content\n', 
    u'##/code-section first\n', 
    u'\n', 
    u'Param modified: FooBarBaz\n']


Jinja templates
---------------

Most of the time you need a little bit more than protected section handling
when building generation templates, such as parameters for dynamic generation.

The Jinja template provides this by handling ``self.template`` as path
to a Jinja template and passes the ``params`` dict of self to the template call.
Protected sections are still handled.

Create some test environment. We need a Jinja template::

    >>> jinjatemplate = u"""
    ... ##code-section first
    ... ##/code-section first
    ... 
    ... Param modified: {{someparam}}
    ... """
    >>> jinjatemplatetarget = os.path.join(tempdir,
    ...                                   'jinjatemplate.txt')
    >>> with codecs.open(jinjatemplatetarget, 'w', encoding='utf-8') as out:
    ...     out.write(jinjatemplate)

And an existing by this template generated file::

    >>> jinjamodified = u"""
    ... ##code-section first
    ... i am the manually created content
    ... ##/code-section first
    ... 
    ... Param modified: Somevalue
    ... """
    >>> jinjamodifiedtarget = os.path.join(tempdir,
    ...                                   'jinjamodified.txt')
    >>> with codecs.open(jinjamodifiedtarget, 'w', encoding='utf-8') as out:
    ...     out.write(jinjamodified)

Create the node based Jinja template::

    >>> from node.ext.template import JinjaTemplate
    >>> jinjatemplate = JinjaTemplate(jinjamodifiedtarget)
    >>> jinjatemplate.template = jinjatemplatetarget
    >>> jinjatemplate
    <node.ext.template.template.JinjaTemplate object at ...>

Check the  Jinja execution::

    >>> jinjatemplate.params['someparam'] = u'Anothervalue'
    >>> jinjatemplate.execjinja()
    [u'\n', 
    u'##code-section first\n', 
    u'##/code-section first\n', 
    u'\n', 
    u'Param modified: Anothervalue\n']

Lets do the handler's ``__call__`` the work::

    >>> jinjatemplate.params['someparam'] = u'FooBarBaz'
    >>> jinjatemplate()
    >>> with codecs.open(jinjamodifiedtarget, 'r', encoding='utf-8') as over:
    ...     over.readlines()
    [u'\n', 
    u'##code-section first\n', 
    u'i am the manually created content\n', 
    u'##/code-section first\n', 
    u'\n', 
    u'Param modified: FooBarBaz\n']


XML Template
------------

This template acts like the DTML template but provides another protected
section pattern, neater for XML.

Create env::

    >>> xmltemplate = u"""
    ... <xml>
    ...   <!-- code-section foo -->
    ...   <!-- /code-section foo -->
    ...   <bar />
    ... </xml>
    ... """
    >>> xmltemplatetarget = os.path.join(tempdir,
    ...                                  'xmltemplate.xml')
    >>> with codecs.open(xmltemplatetarget, 'w', encoding='utf-8') as outfile:
    ...    outfile.write(xmltemplate)

    >>> xmlmodified = u"""
    ... <xml>
    ...   <!-- code-section foo -->
    ...   <foo />
    ...   <!-- /code-section foo -->
    ... </xml>
    ... """
    >>> xmlmodifiedtarget = os.path.join(tempdir,
    ...                                  'xmlmodified.xml')
    >>> with codecs.open(xmlmodifiedtarget, 'w', encoding='utf-8') as outfile:
    ...     outfile.write(xmlmodified)

Create the XML template::

    >>> from node.ext.template import XMLTemplate
    >>> xmltemplate = XMLTemplate(xmlmodifiedtarget)
    >>> xmltemplate.template = xmltemplatetarget
    >>> xmltemplate
    <node.ext.template.template.XMLTemplate object at ...>

Call it and watch the result::

    >>> xmltemplate()
    >>> with codecs.open(xmlmodifiedtarget, 'r', encoding='utf-8') as overwritten:
    ...     overwritten.readlines()
    [u'\n', 
    u'<xml>\n', 
    u'  <!-- code-section foo -->\n', 
    u'  <foo />\n', 
    u'  <!-- /code-section foo -->\n', 
    u'  <bar />\n', u'</xml>\n']

Clean up test Environment::

    >>> import shutil
    >>> shutil.rmtree(tempdir)


ZPTemplate
----------

::
    >>> from node.ext.template import ZPTemplate
    >>> zptemplate = ZPTemplate("""\
    ... <div xmlns="http://www.w3.org/1999/xhtml">
    ...   Hello World!
    ... </div>""")

    >>> print zptemplate()
    <div xmlns="http://www.w3.org/1999/xhtml">
      Hello World!
    </div>
