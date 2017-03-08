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
    url='https://github.com/TabbedOut/django_canary_endpoint',
    license='MIT License',
    packages=find_packages(exclude=('tests', 'docs')),
    test_suite='tests',
    install_requires=[
        'requests>=2.0.0,<3',
        'responses<1',
    ],
    extras_require={
        'rq': ['django_rq<1'],
    },
    classifiers=[
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ],
)
