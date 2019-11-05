"""
    ptime.language
    ~~~~~~~~~~~~~~

    :copyright: (c) 2013 by Marat Ibadinov.
    :license: MIT, see LICENSE for more details.
"""

import os
import json


class Language(object):
    languages = {}

    def __init__(self, month_abbreviations, relative_dates, day_offsets):
        self.month_abbreviations = month_abbreviations
        self.relative_dates = relative_dates
        self.day_offsets = {
            key: set(value)
            for key, value in day_offsets.items()
        }

    def get_month(self, name):
        abbreviation = name[:3]
        return self.month_abbreviations.get(abbreviation)

    def get_offset_for_relative_date(self, relative_date):
        return self.relative_dates.get(relative_date)

    def get_offset_sign(self, offset, prefers_future=False):
        for sign in self.day_offsets:
            if offset in self.day_offsets[sign]:
                return int(sign)

    @classmethod
    def fromcode(cls, code):
        if code in cls.languages:
            return cls.languages[code]
        directory = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(directory, 'languages', '%s.json' % code)
        with open(filename) as stream:
            language = Language(*json.load(stream))
            cls.languages[code] = language
            return language
