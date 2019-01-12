
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
        {"module": "umuus_rest_util", "endpoint": "/PREFIX"},
        {"path": "umuus_rest_util:test_view", "endpoint": "/default"},
        {"path": "umuus_rest_util:test_string_view", "endpoint": "/message"},
        {"path": "umuus_rest_util:test_error_view", "endpoint": "/error"}
    ],
     "server": {
         "host": "0.0.0.0",
         "port": 8003,
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

Table of Contents
-----------------
.. toctree::
   :maxdepth: 2
   :glob:

   *

