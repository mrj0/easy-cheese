from client import client_for_url, ClientTimeoutError
from generator import create_setup
from template import template
import generator

import re
import bottle
from bottle import get, post, static_file, request, route, run, redirect


@get('/')
def display_form():
    return template('form.html', data={})


@get('/manual/')
def display_manual():
    return template('manual.html')


identifiers = re.compile(r'\w+')


def clean_packages(input):
    """
    Take a string of package input, possibly delimited by ',', and
    return a list.
    """
    return re.findall(identifiers, input)


@post('/manual/')
def process_manual():
    setup = generator.SetupDistutils()
    for name in ('name', 'version', 'description', 'long_description',):
        setattr(setup, name, unicode(request.POST.get(name, ''),
                                     "utf-8").strip())

    setup.modules = clean_packages(request.POST.get('modules', ''))
    setup.packages = clean_packages(request.POST.get('packages', ''))

    if not setup.is_valid():
        return template('manual.html',
                        errors=setup.errors,
                        data=request.POST,
                        )

    return template('setup.html', setup=setup.generate())


@post('/')
def process_version_control():
    """ Handles supplied author input and returns setup.py template """

    url = request.POST.get('url')
    if not url:
        return redirect('/manual/')

    try:
        client = client_for_url(url)
        client.fetch()
        setup = create_setup(client)
        return template('setup.html', setup=setup.generate())
    except ClientTimeoutError as te:
        return template('form.html', errors=[te.message], data={})


@route('/static/:filename#.*(\.js|\.css|\.png)#')
def static_serve(filename):
    return static_file(filename, root='static')


def application(environ, start_response):
    return bottle.app()(environ, start_response)

if __name__ == '__main__':
    run(host='localhost', port=8080, reloader=True)
