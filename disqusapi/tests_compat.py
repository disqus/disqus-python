import unittest
import sys

if sys.version_info < (2, 7):
    # Stolen from unittest2
    import re

    class _AssertRaisesBaseContext(object):

        def __init__(self, expected, test_case, callable_obj=None,
                     expected_regex=None):
            self.expected = expected
            self.failureException = test_case.failureException
            if callable_obj is not None:
                try:
                    self.obj_name = callable_obj.__name__
                except AttributeError:
                    self.obj_name = str(callable_obj)
            else:
                self.obj_name = None
            if isinstance(expected_regex, basestring):  # NOQA
                expected_regex = re.compile(expected_regex)
            self.expected_regex = expected_regex

    class _AssertRaisesContext(_AssertRaisesBaseContext):
        """A context manager used to implement TestCase.assertRaises* methods."""

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, tb):
            if exc_type is None:
                try:
                    exc_name = self.expected.__name__
                except AttributeError:
                    exc_name = str(self.expected)
                raise self.failureException(
                    "%s not raised" % (exc_name,))
            if not issubclass(exc_type, self.expected):
                # let unexpected exceptions pass through
                return False
            self.exception = exc_value  # store for later retrieval
            if self.expected_regex is None:
                return True

            expected_regex = self.expected_regex
            if not expected_regex.search(str(exc_value)):
                raise self.failureException(
                    '%r does not match %r' %
                    (expected_regex.pattern, str(exc_value)))
            return True

    class TestCase(unittest.TestCase):
        def assertRaises(self, excClass, callableObj=None, *args, **kwargs):
            """Fail unless an exception of class excClass is thrown
               by callableObj when invoked with arguments args and keyword
               arguments kwargs. If a different type of exception is
               thrown, it will not be caught, and the test case will be
               deemed to have suffered an error, exactly as for an
               unexpected exception.

               If called with callableObj omitted or None, will return a
               context object used like this::

                    with self.assertRaises(SomeException):
                        do_something()

               The context manager keeps a reference to the exception as
               the 'exception' attribute. This allows you to inspect the
               exception after the assertion::

                   with self.assertRaises(SomeException) as cm:
                       do_something()
                   the_exception = cm.exception
                   self.assertEqual(the_exception.error_code, 3)
            """
            if callableObj is None:
                return _AssertRaisesContext(excClass, self)
            try:
                callableObj(*args, **kwargs)
            except excClass:
                return

            if hasattr(excClass, '__name__'):
                excName = excClass.__name__
            else:
                excName = str(excClass)
            raise self.failureException("%s not raised" % excName)
else:
    TestCase = unittest.TestCase
