from client import client_for_url, ClientTimeoutError
from generator import create_setup
from template import template
import generator
import simplejson as json

import re
import bottle
from bottle import get, post, static_file, request, route, run, redirect


@get('/')
def display_form():
    return template('form.html', data={})


identifiers = re.compile(r'\w+')


def clean_packages(input):
    """
    Take a string of package input, possibly delimited by ',', and
    return a list.
    """
    return re.findall(identifiers, input)


def update_setup(data, setup):
    """
    copy data from 'data' dict (request.POST) to setup
    """

    previous = data.get('previous')
    if previous:
        previous = json.loads(previous)
        for name in generator.FIELDS:
            setattr(setup, name, previous.get(name))

    for name in generator.FIELDS:
        value = unicode(data.get(name, ''), "utf-8").strip()
        if value:
            if name in ('modules', 'packages'):
                value = clean_packages(value)
            setattr(setup, name, value)


@post('/')
def process_version_control():
    """ Handles supplied author input and returns setup.py template """

    try:
        url = request.POST.get('repo_url')
        if url:
            client = client_for_url(url)
            client.fetch()
            setup = create_setup(client)
        else:
            setup = create_setup()
            update_setup(request.POST, setup)
    except ClientTimeoutError as te:
        return template('form.html', errors=[te.message], data={})

    return template('setup.html', setup=setup)


@route('/static/:filename#.*(\.js|\.css|\.png)#')
def static_serve(filename):
    return static_file(filename, root='static')


def application(environ, start_response):
    return bottle.app()(environ, start_response)

if __name__ == '__main__':
    run(host='localhost', port=8080, reloader=True)
