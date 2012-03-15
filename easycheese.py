import simplejson as json
from client import client_for_url, ClientTimeoutError
from generator import create_setup, SetupDistutils
from template import template

import bottle
from bottle import get, post, static_file, request, route, run

import logging
log = logging.getLogger(__name__)


@get('/')
def display_form():
    return template('form.html', data={})


@get('/manual/')
def manual():
    return template('setup.html', setup=SetupDistutils())

@post('/')
def process_version_control():
    """ Handles supplied author input and returns setup.py template """

    try:
        url = request.POST.get('repo_url')
        if url:
            client = client_for_url(url, request.POST.get('repo_type'))
            client.fetch()
            setup = create_setup(client)
        else:
            setup = SetupDistutils(formdata=request.POST)
            if request.POST.get('previous'):

                # unfortunately calling form.process applies the json
                # value for all fields. we don't want to overwrite any new
                # values from request.post.

                previous = json.loads(request.POST.get('previous'))
                for name, field, in setup._fields.iteritems():
                    if not field.data:
                        field.process_data(previous.get(name))

                # not a field
                setup.readme = previous.get('readme')

                # license field is a bit strange
                if setup.license.data == 'None':
                    setup.license.data = None

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
