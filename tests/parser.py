# -*- coding: utf-8 -*-

import time
from dateutil.tz import tzoffset
from datetime import date, datetime, timedelta
from unittest import TestCase

from ptime import Parser, ParserError, Format, Language


class TestParserMethods(TestCase):
    def setUp(self):
        self.parser = Parser(Format(''), [Language.fromcode('en')])

    def test_map(self):
        rules = [('a', 'b'), 'c', (lambda a, b: a + b)]
        self.assertEquals(self.parser.map({'a': 1, 'b': 2, 'd': 0}, *rules), {'c': 3, 'd': 0})
        self.assertRaises(ParserError, self.parser.map, {'a': 1}, *rules)
        self.assertRaises(ParserError, self.parser.map, {'a': 1, 'b': 2, 'c': 3}, *rules)

    def test_complete(self):
        now = datetime.now().replace(microsecond=0)
        target = now + timedelta(hours=1)
        attrs = {'hour': target.hour, 'minute': target.minute, 'second': target.second}
        result = self.parser.complete(attrs, now)
        self.assertEquals(datetime(**result), now - timedelta(hours=23))

    def test_parse_weekday(self):
        pass

    def test_parse_yearday(self):
        pass

    def test_parse_month_abbr(self):
        self.assertEquals(self.parser.parse_month_abbr('feb', None), {'month': 2})

    def test_parse_month_name(self):
        self.assertEquals(self.parser.parse_month_abbr('feburary', None), {'month': 2})

    def test_parse_year(self):
        self.assertEquals(self.parser.parse_year('2013', None), {'year': 2013})
        self.assertEquals(self.parser.parse_year('13', None), {'century_year': 13})
        self.assertIsNone(self.parser.parse_year('991', None), None)

    def test_parse_ampm(self):
        self.assertEquals(self.parser.parse_ampm('AM', None), {'ampm': 'am'})

    # timezones are not tested for the sake of perfomance #

    def test_parse_offset_hours(self):
        expectation = {'tzinfo': tzoffset(None, -2*3600 + 30*60)}
        self.assertEquals(self.parser.parse_offset_hours('-02:30', None), expectation)
        self.assertEquals(self.parser.parse_offset_hours('-0230', None), expectation)

    def test_parse_relative_day(self):
        now = datetime.now()
        result = self.parser.parse_relative_day('today', now)
        self.assertEquals(date(**result), now.date())

    def test_parse_days_ago(self):
        now = datetime.now()
        result = self.parser.parse_days_ago('5 days ago', now)
        self.assertEquals(date(**result), now.date() - timedelta(days=5))


class TestParser(TestCase):
    def test_mysql(self):
        now = datetime.now().replace(microsecond=0)
        string = time.strftime('%Y-%m-%d %H:%M:%S', now.timetuple())
        parser = Parser(Format.mysql())
        self.assertEquals(parser.parse(string), now)

    def test_invalid_date(self):
        parser = Parser(Format('%M'))
        self.assertRaises(ParserError, parser.parse, 'abc')

    def test_relative_date(self):
        now = datetime.now()
        parser = Parser(Format('%L'), [Language.fromcode('en')])
        result = parser.parse('yesterday', now)
        self.assertEquals(result.date(), now.date() - timedelta(days=1))

    def test_custom_base(self):
        base = datetime.now().replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
        result = Parser(Format('%i')).parse('30', base)
        self.assertEquals(result, base.replace(minute=30) - timedelta(hours=1))

    def test_completion_boundary_cases(self):
        base = datetime(2013, 9, 13, 1)
        result = Parser(Format('%i')).parse('30', base)
        self.assertEquals(result, datetime(2013, 9, 12, 23, 30))
