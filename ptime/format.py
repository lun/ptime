# -*- coding: utf-8 -*-
"""
    ptime.format
    ~~~~~~~~~~~~

    :copyright: (c) 2013 by Marat Ibadinov.
    :license: MIT, see LICENSE for more details.
"""

import re


class FormatError(Exception):
    pass


class Format(object):
    TEMPLATES = {
        # day #
        'd': (r'\d{2}',                     'day'),
        'D': (r'[a-z]{3}',                  'weekday'),
        'j': (r'(?:[1-9])|(?:[1-3][0-9])',  'day'),
        'l': (ur'[a-zа-я]+',                'weekday'),
        'N': (r'[1-7]',                     'weekday'),
        'w': (r'[0-6]',                     'weekday'),
        'z': (r'\d{3}',                     'yearday'),
        # week #
        # 'W': (r'\d{1,2}',                 None),
        # month #
        'F': (ur'[a-zа-я]+',                'month_name'),
        'm': (r'\d{2}',                     'month'),
        'M': (ur'[a-zа-я]{3}',              'month_abbr'),
        'n': (r'(?:[1-9])|(?:1[0-2])',      'month'),
        # year #
        # 'o': (r'\d{4}',                   'year'), # should correlate with W
        'Y': (r'\d{4}',                     'year'),
        'y': (r'\d{2}',                     'year'),
        'C': (r'\d{2}',                     'century'),
        # time #
        'a': (r'(?:am)|(?:pm)',             'ampm'),
        'A': (r'(?:am)|(?:pm)',             'ampm'),
        'g': (r'\d{1,2}',                   'hour'),
        'G': (r'\d{1,2}',                   'hour'),
        'h': (r'\d{2}',                     'hour'),
        'H': (r'\d{2}',                     'hour'),
        'i': (r'\d{2}',                     'minute'),
        's': (r'\d{2}',                     'second'),
        'u': (r'\d{6}',                     'microsecond'),
        # timezones #
        'e': (r'[a-z\/]+',                  'timezone'),
        'O': (r'[+-]\d{4}',                 'offset_hours'),
        'P': (r'[+-]\d{2}:\d{2}',           'offset_hours'),
        'R': (r'[+-]\d{2}:?\d{2}',          'offset_hours'),
        'T': (r'[a-z]+',                    'timezone'),
        'Z': (r'(?:+?)\d+',                 'offset_seconds'),
        # relative #
        'L': (ur'(?:[a-zа-яіїєґ]+\s?)+',    'relative_day'),
        'K': (ur'\d+\s+(?:[a-zа-я]+\s?)+',  'days_ago')
    }

    def __init__(self, template):
        self.template = template
        regexp, attributes = self.parse_template(template)
        self.regexp = re.compile(r'^%s$' % regexp, re.IGNORECASE | re.UNICODE)
        self.attributes = attributes

    def parse_template(self, template):
        regexp = []
        attributes = []
        had_percent = False
        for character in template:
            if character == '%':
                if had_percent:
                    regexp.append(character)
                had_percent = not had_percent
                continue
            if had_percent:
                if not character in self.TEMPLATES:
                    raise FormatError(
                        "'%{0}' is not a valid template specifier".format(character)
                    )
                pattern, attribute = self.TEMPLATES[character]
                regexp.extend(['(', pattern, ')'])
                attributes.append(attribute)
                had_percent = False
            else:
                regexp.append(character)
        return ''.join(regexp), attributes

    def __eq__(self, other):
        if not isinstance(other, Format):
            return False
        return self.__dict__ == other.__dict__

    @classmethod
    def iso8601(cls):
        # not all variations of ISO-8601 datetime are supported currently
        return cls(r'%Y-%m-%d(?:T|\s)%H:%i(?::%s)?(?:%R)')

    @classmethod
    def rfc822(cls):
        return cls(r'%D, %d %M %Y %H:%i:%s %O')

    @classmethod
    def rfc3339(cls):
        return cls(r'%Y-%m-%dT%H:%i:%s(?:\.%u)?%P')

    @classmethod
    def rfc850(cls):
        return cls(r'%l, %d-%M-%y %H:%i:%s %T')

    @classmethod
    def mysql(cls):
        return cls(r'%Y-%m-%d %H:%i:%s')

    # RFC 822 aliases
    rfc1036 = rfc822
    rfc1123 = rfc822
    rfc2822 = rfc822
    rss     = rfc822

    # RFC 850 aliases
    cookie  = rfc850

    # RFC 3339 aliases
    w3c     = rfc3339
    atom    = rfc3339
