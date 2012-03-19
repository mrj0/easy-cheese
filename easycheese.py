import simplejson as json
import cache
from client import client_for_url, ClientError, CachedClient
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

    url = request.POST.get('repo_url')

    client = None
    setup = None

    # check cache
    if not client and url:
        cached = cache.get(url)
        if cached:
            client = CachedClient(url, cached)
            setup = create_setup(client)

    # attempt to build from version control url
    if not client and url:
        try:
            client = client_for_url(url, request.POST.get('repo_type'))
            client.fetch()
            setup = create_setup(client)
        except (ClientError, IOError):
            log.exception('ignored')

            # failed to get a list of files in repo, but ensure that
            # we can continue manually

            client = None

    # allow manual input
    if not client:
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

    if client:
        client.cache()

    return template('setup.html', setup=setup)


@route('/static/:filename#.*(\.js|\.css|\.png)#')
def static_serve(filename):
    return static_file(filename, root='static')


def application(environ, start_response):
    return bottle.app()(environ, start_response)

if __name__ == '__main__':
    run(host='localhost', port=8080, reloader=True)
