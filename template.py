# -*- coding: utf-8 -*-

import functools
import re
import os
import bottle
import markupsafe  # unused, docs say you must import
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
    return all(ord(c) < 128 for c in s)


identifiers = re.compile(r'\w+')


def clean_identifiers(input):
    """
    Take a string of package input, possibly delimited by ',', and
    return a list.
    """
    return re.findall(identifiers, input)


def pyquote(value):
    if value is None:
        return value

    format = '' if is_ascii(value) else 'u'
    if '\n' in value:
        return u"{format}'''{value}'''".format(
            format=format,
            value=value.replace("'''", "\\'\\'\\'")
        )
    value = value.replace("'", "\\'")
    return u"{format}'{value}'".format(
        format=format,
        value=value,
    )


# filters

def show_field(field, setup):
    name = field.name
    value = field.data

    if name in ('packages', 'modules') and value:
        if isinstance(value, list):
            return '[{}]'.format(', '.join([pyquote(p) for p in value]))

        return '[{}]'.format(
            ', '.join([pyquote(p) for p in clean_identifiers(value)]))

    if name == 'long_description' and setup.readme:
        return 'read_file({})'.format(pyquote(setup.readme))

    if name == 'classifiers' and value:
        return '[\n        {},\n    ]'.format(
            ',\n        '.join([pyquote(c) for c in value]))

    if not value:
        return safe_string('<span class="nocode">{}</span>'.format(field))
    return pyquote(value)
