#!/usr/bin/env python
{% if not under_test %}# -*- coding: utf-8 -*-{% endif %}

from distutils.core import setup
{% if setup.readme %}
import codecs, os
def read_file(name):
    return codecs.open(os.path.join(os.path.dirname(__file__), name),
                       encoding='utf-8').read()
{% endif %}
{% if under_test %}dist = {% endif %}setup({% for field in setup %}
    {{ field.name }}={{ field|show_field(setup, executable) }},
    {%- endfor %}
)
