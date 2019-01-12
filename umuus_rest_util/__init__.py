#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) Jun Makii <junmakii@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""A REST API utility for Python.

umuus-rest-util
===============

Installation
------------

    $ pip install git+https://github.com/junmakii/umuus-rest-util.git

Usage
-----

    $ python DJANGO_APP.py runserver localhost:8000

    $ python umuus_rest_util.py run --paths '["umuus_rest_util:test_view"]' --auth_url 'http://localhost:8000/api/user/'

    $ curl -s http://admin:password@127.0.0.1:5000/umuus_rest_util/test_view
    {"message": "OK"}

----

    $ cat options.json

    {"paths": [
        {"path": "umuus_rest_util:test_view"},
        {"path": "umuus_rest_util:test_string_view", "endpoint": "/message"},
        {"path": "umuus_rest_util:test_error_view", "endpoint": "/error"}
    ],
     "server": {
         "host": "localhost",
         "port": 8033,
         "options": {
             "certfile": "server.crt",
             "keyfile": "server.key"
         }
     },
     "auth_url": "http://0.0.0.0:8000/api/user/"}

    $ python umuus_rest_util.py run --options "$(cat /tmp/options.json)"

    $ curl https://127.0.0.1:8033/umuus_rest_util/test_view

JWT(JSON Web Token)
-------------------

    $ curl -s http://admin:WRONG_PASSWORD@127.0.0.1:5000/umuus_rest_util/test_view
    {"detail":"Invalid username/password."}

    $ token=$(curl -s -X POST -d "username=admin&password=password" http://localhost:8000/jwt-token-auth/ | jq -r '.token')
    $ curl -s -H 'Accept: application/json; indent=4' -H "Authorization: JWT ${token}x" http://localhost:5000/

docker-compose
--------------

options.json::

    {"paths": ["umuus_rest_util:test_view"],
     "server": {
         "host": "0.0.0.0",
         "port": 443,
         "options": {
             "certfile": "/app/server.crt",
             "keyfile": "/app/server.key"
         }
     },
     "auth_url": "http://django:8000/api/user/"}

.env::

    DJANGO_ADDRPORT=0.0.0.0:8000

run.sh::

    python -m umuus_rest_util run --options "$(cat /app/options.json)"

docker-compose.yml::

version: "2"

networks:
  bridge-network:
    driver: bridge

services:
  django:
    build:
      context: .
      dockerfile: Dockerfile.django
    command: ["python", "/app/umuus_django_app.py", "runserver", "${DJANGO_ADDRPORT}"]
    volumes:
      - ".:/app"
    networks:
      - bridge-network
    ports:
      - "6442:8000"
  app:
    build:
      context: .
      dockerfile: Dockerfile.app
    command: ["sh", "/app/run.sh"]
    volumes:
      - ".:/app"
    ports:
      - "6443:4333"
    networks:
      - bridge-network
    depends_on:
      - django

JavaScript with fetch
---------------------

    fetch('http://0.0.0.0:6442/api/user/', {
      mode: 'cors',
      credentials: 'include',
      headers: {"Authorization": "JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluIiwiZXhwIjoxNTQ3MzAyNTYwLCJlbWFpbCI6ImV4YW1wbGVAZXhhbXBsZS5leGFtcGxlIn0.3RvighX8wZ0ppjc29OeUr1rMMRusP87jaWca0p5jVBo"}
    }).then(res => console.log(res))

Authors
-------

- Jun Makii <junmakii@gmail.com>

License
-------

GPLv3 <https://www.gnu.org/licenses/>

"""
import sys
import traceback
import importlib
import json
import functools
import flask
import requests
import requests.auth
import fire
import attr
import addict
import whitenoise
import gunicorn.app.base
__version__ = '0.1'
__url__ = 'https://github.com/junmakii/umuus-rest-util'
__author__ = 'Jun Makii'
__author_email__ = 'junmakii@gmail.com'
__author_username__ = 'junmakii'
__keywords__ = []
__license__ = 'GPLv3'
__scripts__ = []
__install_requires__ = [
    'requests==2.20.1',
    'flask==1.0.2',
    'fire==0.1.3',
    'addict==2.2.0',
    'gunicorn==19.9.0',
    'attrs==18.2.0',
    'whitenoise==4.1.2',
]
__dependency_links__ = []
__classifiers__ = []
__entry_points__ = {
    'console_scripts': ['umuus_rest_util = umuus_rest_util:main'],
    'gui_scripts': [],
}
__project_urls__ = {}
__setup_requires__ = []
__test_suite__ = ''
__tests_require__ = []
__extras_require__ = {}
__package_data__ = {}
__python_requires__ = ''
__include_package_data__ = True
__zip_safe__ = True
__static_files__ = {}
__extra_options__ = {}
__download_url__ = ''


def test_view(**kwargs):
    return dict(message='OK')


def test_string_view(**kwargs):
    return 'OK'


def test_error_view(**kwargs):
    return 0 / 0


def wrapper(fn,
            auth_url='',
            method='GET',
            headers={'Access-Control-Allow-Origin': '*'}):
    @functools.wraps(fn)
    def wrapper():
        try:
            if auth_url:
                res = requests.request(
                    method,
                    auth_url,
                    headers=dict(flask.request.headers),
                    auth=(flask.request.authorization
                          and requests.auth.HTTPBasicAuth(
                              **flask.request.authorization)),
                )
                if res.status_code != 200:
                    return flask.Response(
                        res.text,
                        status=res.status_code,
                        headers=dict(res.headers, **headers),
                    )
            request_params = {
                key: json_encode_value(
                    (value[0] if isinstance(value, list) else value))
                for key, value in (list(flask.request.args.items()) +
                                   list(flask.request.form.items()))
            }
            res = json_encode(fn(**request_params))
            return flask.Response(res, headers=headers)
        except Exception as err:
            traceback.print_exc(file=sys.stderr)
            return flask.Response(
                json.dumps(
                    dict(
                        error=repr(err),
                        reason='\n'.join(
                            traceback.format_exception(*sys.exc_info())))),
                status=500)

    return wrapper


def addict_decorator(fn=None):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return addict.Dict(
            fn(
                *args, **{
                    key: (addict.Dict(value) if isinstance(value, dict)
                          and not isinstance(value, addict.Dict) else value)
                    for key, value in kwargs.items()
                }))

    return (wrapper if fn else functools.partial(addict_decorator))


@addict_decorator()
def import_from_path(data):
    module_name, function_name = data.path.split(':')
    module = importlib.import_module(module_name)
    function = getattr(module, function_name)
    return locals()


def json_encode_value(s):
    try:
        return json.loads(s)
    except Exception:
        return str(s)


def json_encode(d):
    if isinstance(d, (list, tuple)):
        return type(d)(json_encode_value(_) for _ in d)
    elif isinstance(d, dict):
        store = {}
        for key, value in d.items():
            store[key] = json_encode(value)
        return store
    elif isinstance(d, (bool, float, int, type(None))):
        return d
    elif hasattr(d, '__attrs_attrs__'):
        return json_encode(attr.asdict(d))
    else:
        return json_encode_value(d)


@addict_decorator()
def run(options={}):
    app = flask.Flask(__name__)
    items = [import_from_path(item) for item in options.paths]
    for item in items:
        app.route(
            item.data.endpoint
            or '/{}/{}'.format(item.module.__name__, item.function.__name__))(
                wrapper(item.function, auth_url=options.auth_url))
    GunicornServer(application=app.wsgi_app, **options.server).run()


def main(argv=[]):
    fire.Fire()
    return 0


@attr.s()
class GunicornServer(object):
    host = attr.ib('localhost')
    port = attr.ib(0)
    options = attr.ib({
        'bind': '',
        'workers': 1,
        'accesslog': '-',
        'keyfile': '',
        'certfile': '',
    })
    debug = attr.ib(True)
    application = attr.ib(None)
    static_folder = attr.ib(None)
    static_url_path = attr.ib('static')

    def __attrs_post_init__(self):
        self.options['bind'] = (self.options.get('bind')
                                or '%s:%d' % (self.host, self.port))
        self.application = whitenoise.WhiteNoise(
            self.application,
            root=self.static_folder,
            prefix=self.static_url_path,
        )

    def run(self):
        _self = self
        self.gunicorn_app = type(
            'GunicornApplication',
            (gunicorn.app.base.BaseApplication,),
            dict(
                options=self.options,
                load_config=lambda self: [
                    self.cfg.set(key, value)
                    for key, value in self.options.items()
                ],
                load=lambda self: _self.application,
            ))
        self.gunicorn_app().run()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
