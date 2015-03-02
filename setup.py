import os
from setuptools import setup, find_packages


namespace = {}
version_path = os.path.join('canary_endpoint', 'version.py')
exec(open(version_path).read(), namespace)


setup(
    name='django-canary-endpoint',
    version=namespace['__version__'],
    description='Resource health checks for Django.',
    long_description=open('README.md').read(),
    author='TabbedOut',
    author_email='dev@tabbedout.com',
    url='https://github.com/TabbedOut/django-canary-endpoint',
    license=open('LICENSE').read(),
    packages=find_packages(exclude=('tests', 'docs')),
    test_suite='tests',
    install_requires=[
        'django<1.6.0',
        'django-rq>=0.7.0',
        'requests>=2.0.0',
    ]
)
