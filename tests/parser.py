import time

from dateutil.tz import tzoffset
from datetime import date, datetime, timedelta
from unittest import TestCase

from ptime import Parser, ParserError, Format, Language


class TestParserMethods(TestCase):
    def setUp(self):
        self.parser = Parser(Format(''), [Language.fromcode('en')])

    def test_complete(self):
        now = datetime.now(tzoffset(None, 0)).replace(microsecond=0)
        target = now + timedelta(hours=1)
        attrs = {
            'hour': target.hour,
            'minute': target.minute,
            'second': target.second,
        }
        result = self.parser.complete(attrs, now)
        self.assertEqual(
            self.parser.mktime(result), now - timedelta(hours=23))

    def test_parse_weekday(self):
        pass

    def test_parse_yearday(self):
        pass

    def test_parse_month_abbr(self):
        self.assertEqual(
            self.parser.parse_month_abbr('feb', None), {'month': 2})

    def test_parse_month_name(self):
        self.assertEqual(
            self.parser.parse_month_name('feburary', None), {'month': 2})

    def test_parse_ampm(self):
        self.assertEqual(self.parser.parse_ampm('PM', None), {'ampm': 1})

    # timezones are not tested for the sake of perfomance #

    def test_parse_offset_hours(self):
        expectation = {'tzinfo': tzoffset(None, -2*3600 + 30*60)}
        self.assertEqual(
            self.parser.parse_offset_hours('-02:30', None), expectation)
        self.assertEqual(
            self.parser.parse_offset_hours('-0230', None), expectation)

    def test_parse_relative_day(self):
        now = datetime.now()
        result = self.parser.parse_relative_day('today', now)
        self.assertEqual(date(**result), now.date())

    def test_parse_days_ago(self):
        now = datetime.now()
        result = self.parser.parse_days_ago('5 days ago', now)
        self.assertEqual(date(**result), now.date() - timedelta(days=5))


class TestParser(TestCase):
    def test_mysql(self):
        now = datetime.now().replace(microsecond=0)
        string = time.strftime('%Y-%m-%d %H:%M:%S', now.timetuple())
        parser = Parser(Format.mysql())
        self.assertEqual(parser.parse(string), now)

    def test_invalid_date(self):
        parser = Parser(Format('%M'))
        self.assertRaises(ParserError, parser.parse, 'abc')

    def test_relative_date(self):
        now = datetime.now()
        parser = Parser(Format('%L'), [Language.fromcode('en')])
        result = parser.parse('yesterday', now)
        self.assertEqual(result.date(), now.date() - timedelta(days=1))

    def test_custom_base(self):
        base = datetime.now().replace(minute=0, second=0, microsecond=0) - \
               timedelta(hours=1)
        result = Parser(Format('%i')).parse('30', base)
        self.assertEqual(result, base.replace(minute=30) - timedelta(hours=1))

    def test_completion_boundary_cases(self):
        base = datetime(2013, 9, 13, 0)
        result = Parser(Format('%i')).parse('30', base)
        self.assertEqual(result, datetime(2013, 9, 12, 23, 30))

    def test_century_year(self):
        result = Parser(Format('%d.%m.%y')).parse('30.10.13')
        self.assertEqual(result.date(), date(2013, 10, 30))
