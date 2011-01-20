import unittest
import doctest
import zope.component
from pprint import pprint
from interlude import interact
from zope.configuration.xmlconfig import XMLConfig

optionflags = doctest.NORMALIZE_WHITESPACE | \
              doctest.ELLIPSIS | \
              doctest.REPORT_ONLY_FIRST_FAILURE

TESTFILES = [
    '../codesectionhandler.txt',
    '../_api.txt',
]


def test_suite():
    XMLConfig('meta.zcml', zope.component)()

    return unittest.TestSuite([
        doctest.DocFileSuite(
            file,
            optionflags=optionflags,
            globs={'interact': interact,
                   'pprint': pprint},
        ) for file in TESTFILES])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
