# -*- coding: utf-8 -*-
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
        self.day_offsets = {key: set(value) for key, value in day_offsets.iteritems()}

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
    def fromcode(self, code):
        if code in self.languages:
            return self.languages[code]
        directory = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(directory, 'languages', '%s.json' % code)
        with open(filename) as stream:
            language = Language(*json.load(stream))
            self.languages[code] = language
            return language
