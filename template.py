# -*- coding: utf-8 -*-

import functools
import re
import os
import bottle
from markupsafe import escape
import jinja2

bottle.debug()
bottle.TEMPLATE_PATH.append(os.path.join(os.path.dirname(__file__),
                                         'templates'))
safe_string = jinja2.Markup


class CustomJinja2Template(bottle.Jinja2Template):
    def prepare(self, filters=None, tests=None, **kwargs):
        kwargs['autoescape'] = True
        filters = {'show_field': show_field}
        return super(CustomJinja2Template, self).prepare(
            filters=filters, tests=tests, **kwargs)


template = functools.partial(bottle.template,
                             template_adapter=CustomJinja2Template)


def is_ascii(s):
    if not s:
        return True
    try:
        s.decode('ascii')
        return True
    except UnicodeEncodeError:
        return False


def pyquote(value):
    if value is None:
        return value

    if is_ascii(value):
        escaped = repr(str(value)).decode('string_escape')
    else:
        escaped = unicode(repr(value).decode('unicode_escape'))

    if '\n' in escaped:
        return u"'''{}'''".format(escaped[1:-1].replace("'''", r"\'''"))
    return escaped


def no_code(value):
    return u'<span class="nocode">{}</span>'.format(value)


# filters

def show_field(field, setup, executable):
    name = field.name
    value = field.data
    formatted = None

    if name in ('packages', 'py_modules', 'requires') and value:
        formatted = '[{}]'.format(', '.join(
            [pyquote(p) for p in field.as_list()]))

    elif name == 'long_description':
        if setup.readme.data:
            return '{}=read_file({})'.format(
                field.name,
                pyquote(setup.readme.data))

    elif name == 'classifiers' and value:
        formatted = \
            '[\n        {},\n    ]'.format(
            ',\n        '.join([pyquote(c) for c in value]))

    if not formatted:
        formatted = pyquote(value)

    if executable:
        if value is None:
            return ''
        return u'{}={},'.format(field.name, formatted)

    if not value:
        return safe_string(u'{}={},'.format(
            field.name,
            no_code(field),
        ))

    # make sure the actual value for these fields as displayed in the hidden
    # field parses correctly
    if name in ('requires',) and isinstance(value, list):
        field.data = ' '.join(value)

    return safe_string(u'<span class="line">{}=<span class="value">{}</span>' \
                       u'<span class="edit">{}</span>,</span>'.format(
        field.name,
        escape(formatted),
        no_code(field),
    ))
