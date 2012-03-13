#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup({% for key, value in setup.required() %}
    {{ key }}={{ value|pyquote }},{% endfor %}
    {% if setup.modules %}modules=[{{ setup.module_str }}],{% endif %}
    {% if setup.packages %}packages=[{{ setup.package_str }}],{% endif %}
)
