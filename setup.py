
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def run_tests(self):
        import sys
        import shlex
        import pytest
        errno = pytest.main(['--doctest-modules'])
        if errno != 0:
            raise Exception('An error occured during installution.')
        install.run(self)


setup(
    packages=setuptools.find_packages('.'),
    version='0.1',
    url='https://github.com/junmakii/umuus-rest-util',
    author='Jun Makii',
    author_email='junmakii@gmail.com',
    keywords=[],
    license='GPLv3',
    scripts=[],
    install_requires=['requests==2.20.1',
 'flask==1.0.2',
 'fire==0.1.3',
 'addict==2.2.0',
 'gunicorn==19.9.0',
 'attrs==18.2.0'],
    dependency_links=[],
    classifiers=[],
    entry_points={'console_scripts': ['umuus_rest_util = umuus_rest_util:main'],
 'gui_scripts': []},
    project_urls={},
    setup_requires=[],
    test_suite='',
    tests_require=[],
    extras_require={},
    package_data={},
    python_requires='',
    include_package_data=True,
    zip_safe=True,
    name='umuus-rest-util',
    description='A REST API utility for Python.',
    long_description=('A REST API utility for Python.\n'
 '\n'
 'umuus-rest-util\n'
 '===============\n'
 '\n'
 'Installation\n'
 '------------\n'
 '\n'
 '    $ pip install git+https://github.com/junmakii/umuus-rest-util.git\n'
 '\n'
 'Usage\n'
 '-----\n'
 '\n'
 '    $ python DJANGO_APP.py runserver localhost:8000\n'
 '\n'
 '    $ python umuus_rest_util.py run --paths '
 '\'["umuus_rest_util:test_view"]\' --auth_url '
 "'http://localhost:8000/api/user/'\n"
 '\n'
 '    $ curl -s '
 'http://admin:password@127.0.0.1:5000/umuus_rest_util/test_view\n'
 '    {"message": "OK"}\n'
 '\n'
 '$ cat options.json\n'
 '\n'
 '{"paths": ["umuus_rest_util:test_view"],\n'
 ' "server": {\n'
 '     "host": "localhost",\n'
 '     "port": 8033,\n'
 '     "options": {\n'
 '         "certfile": "server.crt",\n'
 '         "keyfile": "server.key"\n'
 '     }\n'
 ' },\n'
 ' "auth_url": "http://0.0.0.0:8000/api/user/"}\n'
 '\n'
 '$ python umuus_rest_util.py run --options "$(cat /tmp/options.json)"\n'
 '\n'
 'curl https://127.0.0.1:8033/umuus_rest_util/test_view\n'
 '\n'
 'JWT(JSON Web Token)\n'
 '-------------------\n'
 '\n'
 '    $ curl -s '
 'http://admin:WRONG_PASSWORD@127.0.0.1:5000/umuus_rest_util/test_view\n'
 '    {"detail":"Invalid username/password."}\n'
 '\n'
 '    $ token=$(curl -s -X POST -d "username=admin&password=password" '
 "http://localhost:8000/jwt-token-auth/ | jq -r '.token')\n"
 '    $ curl -s -H \'Accept: application/json; indent=4\' -H "Authorization: '
 'JWT ${token}x" http://localhost:5000/\n'
 '\n'
 'Authors\n'
 '-------\n'
 '\n'
 '- Jun Makii <junmakii@gmail.com>\n'
 '\n'
 'License\n'
 '-------\n'
 '\n'
 'GPLv3 <https://www.gnu.org/licenses/>'),
    cmdclass={"pytest": PyTest},
)
