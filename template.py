# -*- coding: utf-8 -*-

import functools
import os
import bottle
import markupsafe # unused, docs say you must import
import jinja2

bottle.debug()
bottle.TEMPLATE_PATH.append(os.path.join(os.path.dirname(__file__),
                                         'templates'))
safe_string = jinja2.Markup

class CustomJinja2Template(bottle.Jinja2Template):
    def prepare(self, filters=None, tests=None, **kwargs):
        kwargs['autoescape'] = True
        filters = {'pyquote': pyquote, 'placeholder': placeholder}
        return super(CustomJinja2Template, self).prepare(filters=filters, tests=tests, **kwargs)


template = functools.partial(bottle.template, template_adapter=CustomJinja2Template)


def is_ascii(s):
    if not s:
        return True
    return all(ord(c) < 128 for c in s)

# filters

def pyquote(value):
    if value is None:
        return None
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


def placeholder(value, name):
    if value is not None:
        return value
    return safe_string('<input name="{}" type="text">'.format(jinja2.escape(name)))