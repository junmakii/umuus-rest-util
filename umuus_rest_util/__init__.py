#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C)    <junmakii@gmail.com>
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

$ cat options.json

{"paths": ["umuus_rest_util:test_view"],
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

curl https://127.0.0.1:8033/umuus_rest_util/test_view

JWT(JSON Web Token)
-------------------

    $ curl -s http://admin:WRONG_PASSWORD@127.0.0.1:5000/umuus_rest_util/test_view
    {"detail":"Invalid username/password."}

    $ token=$(curl -s -X POST -d "username=admin&password=password" http://localhost:8000/jwt-token-auth/ | jq -r '.token')
    $ curl -s -H 'Accept: application/json; indent=4' -H "Authorization: JWT ${token}x" http://localhost:5000/

Authors
-------

- Jun Makii <junmakii@gmail.com>

License
-------

GPLv3 <https://www.gnu.org/licenses/>

"""
import sys
import importlib
import json
import functools
import flask
import requests
import requests.auth
import fire
import attr
import addict
import gunicorn.app.base
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018  Jun Makii <junmakii@gmail.com>
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
"""Utilities, tools, and scripts for Python.

umuus-rest-util
===============

Installation
------------

    $ pip install git+https://github.com/junmakii/umuus-rest-util.git

Example
-------

    $ umuus_rest_util

    >>> import umuus_rest_util



Authors
-------

- Jun Makii <junmakii@gmail.com>

License
-------

GPLv3 <https://www.gnu.org/licenses/>

"""
import sys
import json
import functools
import logging
logger = logging.getLogger(__name__)
import fire
import attr
import addict
import requests
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


def auth_wrapper(fn, auth_url='', method='GET'):
    @functools.wraps(fn)
    def wrapper():
        try:
            res = requests.request(
                method,
                auth_url,
                headers=dict(flask.request.headers),
                auth=(flask.request.authorization
                      and requests.auth.HTTPBasicAuth(
                          **flask.request.authorization)),
            )
            request_params = {
                key: json_encode_value(
                    (value[0] if isinstance(value, list) else value))
                for key, value in (list(flask.request.args.items()) +
                                   list(flask.request.form.items()))
            }
            if res.status_code == 200:
                return json.dumps(fn(**request_params))
            else:
                return flask.Response(
                    res.text,
                    status=res.status_code,
                    headers=dict(res.headers),
                )
        except Exception as err:
            import traceback
            traceback.print_exc(file=sys.stderr)
            return flask.Response(str(err), status=500)

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
def import_from_path(path):
    module_name, function_name = path.split(':')
    module = importlib.import_module(module_name)
    function = getattr(module, function_name)
    return locals()


def json_encode_value(s):
    try:
        return json.loads(s)
    except Exception:
        return str(s)


@addict_decorator()
def run(options={}):
    app = flask.Flask(__name__)
    items = [import_from_path(path) for path in options.paths]
    for item in items:
        app.route('/{}/{}'.format(
            item.module.__name__, item.function.__name__))(auth_wrapper(
                item.function, auth_url=options.auth_url))
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
    static_url_path = attr.ib('')

    def __attrs_post_init__(self):
        self.options['bind'] = (self.options.get('bind')
                                or '%s:%d' % (self.host, self.port))

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
