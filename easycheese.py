from gevent import monkey; monkey.patch_all()
import simplejson as json
import cache
from client import client_for_url, ClientError, CachedClient
from generator import create_setup, SetupDistutils
from template import template

import bottle
from bottle import get, post, static_file, request, route, run, redirect, HTTPResponse

import logging
log = logging.getLogger(__name__)


@get('/')
def display_form():
    return template('form.html', data={})


@get('/manual/')
def display_manual():
    setup = SetupDistutils()
    return redirect('/setup/{}/'.format(setup.cache_key))


@post('/')
def process():
    """ Handles supplied author input and returns setup.py template """

    url = request.POST.get('repo_url')

    client = None
    setup = None

    cached = cache.get(cache.make_key(url))
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

    if client:
        client.cache()
    if setup:
        setup.cache()
    else:
        setup = SetupDistutils()

    yield redirect('/setup/{}/'.format(setup.cache_key))


@get('/setup/:key#[a-fA-F0-9]+#/setup.py')
def view_executable(key):
    data = {}
    data.update(json.loads(cache.get(key, default='{}')))

    setup = SetupDistutils(**data)
    setup.cache_key = key
    setup.validate()

    return HTTPResponse(
        setup.generate(executable=True),
        header={'Content-type': 'text/x-python'},
    )


@get('/setup/:key#[a-fA-F0-9]+#/')
@post('/setup/:key#[a-fA-F0-9]+#/')
def view_setup(key):
    data = {}
    data.update(json.loads(cache.get(key, default='{}')))

    # can't update the dictionary because normal dict access
    # doesn't return unicode strings in FormDict
    #    data.update(request.POST)
    for k in request.POST.keys():
        data[k] = request.POST.getunicode(k)
    data['classifiers'] = request.POST.getlist('classifiers')

    setup = SetupDistutils(**data)
    setup.cache_key = key
    setup.validate()
    setup.cache()

    if 'save' in request.POST:
        return redirect(request.path + 'setup.py')
    return template('setup.html', setup=setup)


@route('/static/:filename#.*(\.js|\.css|\.png)#')
def static_serve(filename):
    return static_file(filename, root='static')


def application(environ, start_response):
    return bottle.app()(environ, start_response)

if __name__ == '__main__':
    # register version control backends
    import pip
    pip.version_control()

    # see http://bottlepy.org/docs/stable/async.html
    run(host='localhost',
        port=8000,
        reloader=True,
        server='gevent',
    )
