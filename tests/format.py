# -*- coding: utf-8 -*-

import re
import time
from datetime import datetime
from unittest import TestCase

from ptime import Format, FormatException


class TestFormat(TestCase):
    def test_qualifiers(self):
        regexp = Format('').regexp
        self.assertEquals(regexp, re.compile(r'^$', re.IGNORECASE))

    def test_escaping(self):
        regexp, attrs = Format('').parse_template('%%%%')
        self.assertEquals(regexp, '%%')

    def test_invalid_template(self):
        self.assertRaises(FormatException, Format, '%~')

    def test_basic_format(self):
        regexp = Format('%Y-%m-%d').regexp
        self.assertIsNotNone(re.match(regexp, '2013-09-10'))


class TestStandardFormats(TestCase):
    def test_iso8601(self):
        regexp = Format.iso8601().regexp
        self.assertIsNotNone(re.match(regexp, '2013-09-11T18:44:25+03:00'))

    def test_rfc822(self):
        regexp = Format.rfc822().regexp
        self.assertIsNotNone(re.match(regexp, 'Wed, 11 Sep 2013 15:53:02 -0000'))

    def test_rfc3339(self):
        regexp = Format.rfc3339().regexp
        self.assertIsNotNone(re.match(regexp, '2013-09-11T19:13:02+03:00'))

    def test_rfc850(self):
        regexp = Format.rfc850().regexp
        self.assertIsNotNone(re.match(regexp, 'Wednesday, 11-Sep-13 19:15:03 EEST'))

    def test_mysql(self):
        regexp = Format.mysql().regexp
        self.assertIsNotNone(re.match(regexp, '2013-09-11 19:17:39'))


class TestShorthandMethods(TestCase):
    def test_rfc1036(self):
        self.assertEquals(Format.rfc1036(), Format.rfc822())

    def test_rfc1123(self):
        self.assertEquals(Format.rfc1123(), Format.rfc822())

    def test_rfc2822(self):
        self.assertEquals(Format.rfc2822(), Format.rfc822())

    def test_rss(self):
        self.assertEquals(Format.rss(), Format.rfc822())

    def test_cookie(self):
        self.assertEquals(Format.cookie(), Format.rfc850())

    def test_w3c(self):
        self.assertEquals(Format.w3c(), Format.rfc3339())

    def test_atom(self):
        self.assertEquals(Format.atom(), Format.rfc3339())
