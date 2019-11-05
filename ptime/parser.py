"""
    ptime.parser
    ~~~~~~~~~~~~

    :copyright: (c) 2013 by Marat Ibadinov.
    :license: MIT, see LICENSE for more details.
"""

from . import completion

import re

from datetime import datetime, timedelta
from pytz import timezone
from dateutil.tz import tzoffset


class ParserError(Exception):
    pass


class Parser(object):
    INTEGER_ATTRIBUTES = [
        'year',
        'month',
        'day',
        'hour',
        'minute',
        'second',
        'microsecond',
    ]

    def __init__(self, format, languages=None, prefers_future=False):
        self.format = format
        self.languages = languages or []
        self.prefers_future = prefers_future

    def parse(self, string, base=None):
        base = base or datetime.now()
        match = re.match(self.format.regexp, string)
        if not match:
            return None

        parts = {}
        for index, value in enumerate(match.groups()):
            part = self.format.attributes[index]
            parser = 'parse_%s' % part
            if hasattr(self, parser):
                components = getattr(self, parser)(value, base)
                if components is None:
                    raise ParserError("Failed to parse %r" % part)
                parts.update(components)
            elif part in self.INTEGER_ATTRIBUTES:
                parts[part] = int(value)
            else:
                raise ParserError("Unsupported attribute %r" % part)

        return self.mktime(self.complete(parts, base))

    def mktime(self, parts):
        return completion.mktime(parts)

    def complete(self, parts, base):
        parts = completion.unpack(parts)
        if self.prefers_future:
            return completion.complete_future(parts, base)
        return completion.complete_past(parts, base)

    def parse_weekday(self, value, base):
        # todo
        return {}

    def parse_yearday(self, value, base):
        # todo
        return {}

    def parse_month_abbr(self, value, base):
        value = value.lower()
        for language in self.languages:
            month = language.get_month(value)
            if month:
                return {'month': month}

    def parse_month_name(self, value, base):
        return self.parse_month_abbr(value[:3], base)

    def parse_ampm(self, value, base):
        result = 1 if value.lower() == 'pm' else 0
        return {'ampm': result}

    def parse_timezone(self, value, base):
        return {'tzinfo': timezone(value)}

    def parse_offset_seconds(self, value, base):
        return {'tzinfo': tzoffset(None, int(value))}

    def parse_offset_hours(self, value, base):
        value = value.replace(':', '')
        offset = int(value[:3]) * 3600 + int(value[3:]) * 60
        return {'tzinfo': tzoffset(None, offset)}

    def parse_relative_day(self, value, base):
        value = value.lower().strip()
        for language in self.languages:
            delta_days = language.get_offset_for_relative_date(value)
            if delta_days is not None:
                date = base.date() + timedelta(delta_days)
                return {
                    'year': date.year,
                    'day': date.day,
                    'month': date.month,
                }

    def parse_days_ago(self, value, base):
        parts = value.split()
        absolute_delta = int(parts[0])
        words = ' '.join(word.lower() for word in parts[1:])
        for language in self.languages:
            sign = language.get_offset_sign(words, self.prefers_future)
            if sign:
                date = base.date() + timedelta(sign * absolute_delta)
                return {
                    'year': date.year,
                    'day': date.day,
                    'month': date.month,
                }
