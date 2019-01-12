
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

Table of Contents
-----------------
.. toctree::
   :maxdepth: 2
   :glob:

   *

