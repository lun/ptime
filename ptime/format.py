# -*- coding: utf-8 -*-
"""
    ptime.format
    ~~~~~~~~~~~~

    :copyright: (c) 2013 by Marat Ibadinov.
    :license: MIT, see LICENSE for more details.
"""

import re


class FormatException(Exception):
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
        'g': (r'\d{1,2}',                   'hour_ampm'),
        'G': (r'\d{1,2}',                   'hour'),
        'h': (r'\d{2}',                     'hour_ampm'),
        'H': (r'\d{2}',                     'hour'),
        'i': (r'\d{2}',                     'minute'),
        's': (r'\d{2}',                     'second'),
        'u': (r'\d{2}',                     'microsecond'),
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
        self.regexp = re.compile(r'^%s$' % regexp, re.IGNORECASE)
        self.attributes = attributes

    def parse_template(self, template):
        regexp = []
        attributes = []
        had_percent = False
        previous = None
        for character in template:
            if character == '%':
                if had_percent:
                    regexp.append(character)
                had_percent = not had_percent
            else:
                if had_percent:
                    if not character in self.TEMPLATES:
                        raise FormatException(
                            "'%{0}' is not a valid template specifier".format(character)
                        )
                    pattern, attribute = self.TEMPLATES[character]
                    regexp.extend(['(', pattern, ')'])
                    attributes.append(attribute)
                    had_percent = False
                else:
                    regexp.append(character)
        return (''.join(regexp), attributes)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    @classmethod
    def iso8601(self):
        # not all variations of ISO-8601 datetime are supported currently
        return Format(r'%Y-%m-%d(?:T|\s)%H:%i(?::%s)?(?:%R)')

    @classmethod
    def rfc822(self):
        return Format(r'%D, %d %M %Y %H:%i:%s %O')

    @classmethod
    def rfc3339(self):
        return Format(r'%Y-%m-%dT%H:%i:%s%P')

    @classmethod
    def rfc850(self):
        return Format(r'%l, %d-%M-%y %H:%i:%s %T')

    @classmethod
    def mysql(self):
        return Format(r'%Y-%m-%d %H:%i:%s')

    # RFC 822 aliases #

    @classmethod
    def rfc1036(self):
        return self.rfc822()

    @classmethod
    def rfc1123(self):
        return self.rfc822()

    @classmethod
    def rfc2822(self):
        return self.rfc822()

    @classmethod
    def rss(self):
        return self.rfc822()

    # RFC 850 aliases #

    @classmethod
    def cookie(self):
        return self.rfc850()

    # RFC 3339 aliases #

    @classmethod
    def w3c(self):
        return self.rfc3339()

    @classmethod
    def atom(self):
        return self.rfc3339()
