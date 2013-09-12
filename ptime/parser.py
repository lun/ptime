# -*- coding: utf-8 -*-
"""
    ptime.parser
    ~~~~~~~~~~~~

    :copyright: (c) 2013 by Marat Ibadinov.
    :license: MIT, see LICENSE for more details.
"""

import re

from datetime import datetime, timedelta
from pytz import timezone
from dateutil.tz import tzoffset


class ParserError(Exception):
    pass


class Parser(object):
    INTEGER_ATTRIBUTES = ['year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond']
    ATTRIBUTE_ORDER = ['second', 'minute', 'hour', 'day', 'month', 'year']

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
                    raise ParserError("Failed to parse '%s'" % part)
                present = [key for key in components if key in parts]
                parts.update(components)
            elif part in self.INTEGER_ATTRIBUTES:
                parts[part] = int(value)
            else:
                raise ParserError("Unsupported attribute '%s'" % part)

        parts = self.compose(parts)
        parts = self.complete(parts, base)
        return self.construct_datetime(parts)

    def map(self, parts, sources, destination, func):
        present = filter(parts.has_key, sources)
        if not present:
            return parts
        if len(present) < len(sources):
            raise ParserError("{0} can't be present without {1}",
                ', '.join(present), ', '.join(set(sources) - set(present))
            )
        if destination in parts:
            raise ParserError("{0} can't be present simultaneously with {1}",
                destination, ', '.join(sources)
            )
        result = {key: value for key, value in parts.iteritems() if key not in sources}
        result[destination] = func(*[parts[key] for key in sources])
        return result

    def compose(self, parts):
        parts = self.map(parts, ('century', 'century_year'), 'year', lambda x, y: x * 100 + y)
        parts = self.map(parts, ('hour_ampm', 'ampm'), 'hour', lambda x, y: x + [0, 12][y=='pm'])
        return parts

    def complete(self, parts, base):
        useful = self.ATTRIBUTE_ORDER + ['tzinfo']
        result = {attr: parts[attr] if attr in parts else getattr(base, attr) for attr in useful}

        for attr in self.ATTRIBUTE_ORDER:
            if parts.get(attr):
                continue
            while True:
                timestamp = self.construct_datetime(result)
                # todo: use self.prefers_future
                if timestamp <= base or result[attr] == 0:
                    break
                result[attr] -= 1
        return result

    def construct_datetime(self, parts):
        return datetime(**parts)

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
        return {'month': self.parse_month_abbr(value[:3])}

    def parse_year(self, value, base):
        digits = len(str(value))
        if digits == 4:
            return {'year': int(value)}
        if digits == 2:
            return {'century_year': int(value)}

    def parse_ampm(self, value, base):
        return {'ampm': value.lower()}

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
                return {'year': date.year, 'day': date.day, 'month': date.month}

    def parse_days_ago(self, value, base):
        parts = re.split(r'\s+', value)
        absolute_delta = int(parts[0])
        words = ' '.join(word.lower() for word in parts[1:])
        delta_days = None
        for language in self.languages:
            sign = language.get_offset_sign(words, self.prefers_future)
            if sign:
                date = base.date() + timedelta(sign * absolute_delta)
                return {'year': date.year, 'day': date.day, 'month': date.month}
