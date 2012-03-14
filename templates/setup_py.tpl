#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
{% if setup.readme %}
import codecs, os
def read_file(name):
    return codecs.open(os.path.join(os.path.dirname(__file__), name),
                       encoding='utf-8').read()
{% endif %}
setup({% for key, value in setup.setup_fields %}
    {{ key }}={{ value|pyquote }},{% endfor %}
    {% if setup.modules %}py_modules=[{{ setup.module_str }}],
    {% endif %}{% if setup.packages %}packages=[{{ setup.package_str }}],{% endif %}
    {% if setup.readme %}long_description=read_file({{ setup.readme|pyquote }}),{% endif %}
)
