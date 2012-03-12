import re
import os

import bottle
from bottle import get, post, static_file, request, route, run, view
from bottle import jinja2_template as template

bottle.debug()
bottle.TEMPLATE_PATH.append(os.path.join(os.path.dirname(__file__),
                                         'templates'))


@get('/')
def display_form():
    return template('form.html')


@post('/')
@view('setupdotpy_out')
def process_form():
    """ Handles supplied user input and returns setup.py template """

    # regexes to help clear user input of extraneous chars
    cruft = re.compile('(\.py|\"|\')')
    newlines = re.compile('(\n|\r\n|\r)')

    modules = request.forms.get('modules')
    packages = request.forms.get('packages')

    def format_apps(app_str):
        """ Strips out cruft from user input and returns formatted string """
        apps_clear = re.sub(cruft, '', app_str)
        apps = re.sub(newlines, "', '", apps_clear)

        return apps

    return {
        # Short strings should be no more than 200 chars
        'name': request.forms.get('name')[:200],
        'version': request.forms.get('version')[:200],

        'description': request.forms.get('description'),
        'long_description': request.forms.get('long_description'),
        'modules': format_apps(modules),
        'packages': format_apps(packages),
    }


@route('/download/setup.py')
def download():
    return static_file('setup\.py', download='setup.py')


@route('/static/:filename#.*(\.js|\.css)#')
def static_serve(filename):
    return static_file(filename, root='static')


def application(environ, start_response):
    return bottle.app()(environ, start_response)

if __name__ == '__main__':
    run(host='localhost', port=8080)
