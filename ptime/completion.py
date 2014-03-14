# -*- coding: utf-8 -*-
"""
    ptime.completion
    ~~~~~~~~~~~~~~~~

    :copyright: (c) 2013 by Marat Ibadinov.
    :license: MIT, see LICENSE for more details.
"""

from calendar import monthrange
from datetime import datetime


ATTRIBUTES = ['century', 'year', 'month', 'day', 'ampm', 'hour', 'minute', 'second']
MINIMUMS = {
    'century': 19, 'year': 0, 'month': 1, 'day': 1, 'ampm': 0, 'hour': 0, 'minute': 0, 'second': 0
}
MAXIMUMS = {
    'century': 20, 'year': 99, 'month': 12, 'ampm': 1, 'hour': 11, 'minute': 59, 'second': 0
}


def get_min(attribute, parts):
    return MINIMUMS[attribute]


def get_max(attribute, parts):
    if attribute == 'day':
        return monthrange(parts['year'], parts['month'])[1]
    return MAXIMUMS[attribute]


def pack(parts):
    result = {attr: value for attr, value in parts.items() if attr not in ['century', 'ampm']}
    result['year'] = parts['century'] * 100 + parts['year']
    result['hour'] = [0, 12][parts['ampm']] + parts['hour']
    return result


def unpack(parts):
    result = dict(parts)
    hour = parts.get('hour')
    if hour:
        result['hour'], result['ampm'] = (hour - 12, 1) if hour > 12 else (hour, 0)
    year = parts.get('year')
    if year:
        if year > 100:
            result['year'], result['century'] = (year % 100, year / 100)
        else:
            result['year'] = year
    return result


def mktime(parts):
    return datetime(**pack(parts))


def fill(parts, get_default):
    copy = {}
    for attr in ATTRIBUTES:
        copy[attr] = parts[attr] if attr in parts else get_default(attr, copy)
    for attr in parts:
        copy[attr] = copy[attr] if attr in copy else parts[attr]
    return copy


def complete_past(parts, base):
    parts['tzinfo'] = parts.get('tzinfo') or base.tzinfo
    parts = dict(parts)
    for attribute in ATTRIBUTES:
        if attribute in parts:
            continue
        copy = fill(parts, get_min)
        bound = get_max(attribute, copy)
        parts[attribute] = copy[attribute]
        while parts[attribute] < bound and mktime(copy) < base:
            parts[attribute] += 1
            copy = fill(parts, get_min)
        if mktime(copy) > base:
            parts[attribute] -= 1
    return parts


def complete_future(parts, base):
    parts['tzinfo'] = parts.get('tzinfo') or base.tzinfo
    parts = dict(parts)
    for attribute in ATTRIBUTES:
        if attribute in parts:
            continue
        copy = fill(parts, get_max)
        bound = get_min(attribute, copy)
        parts[attribute] = copy[attribute]
        while parts[attribute] > bound and mktime(copy) > base:
            parts[attribute] -= 1
            copy = fill(parts, get_max)
        if mktime(copy) < base:
            parts[attribute] += 1
    return parts
