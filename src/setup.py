import sys
from setuptools import find_packages, setup

setup(
    name='pdnsadm',
    version='0.1',
    python_requires='>=3.7',
    description='Admin interface for PowerDNS.',
    author='uberspace.de',
    author_email='hallo@uberspace.de',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.1',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    keywords='dns powerdns pdns admin administration',
    install_requires=[
        'Django==2.1.*',
        'dj-database-url==0.5.*',
        'requests',  # should be installed with python-powerdns ... ?
        'python-powerdns@https://github.com/vente-privee/python-powerdns/archive/1c61c574399e3e486a6e0b9d1e3d0521b2fa00a0.zip',
    ],
    extras_require={
        'dev': [
            'beautifulsoup4',
            'isort',
            'lxml',
            'pylama',
            'pytest',
            'pytest-cov',
            'pytest-django',
        ],
    },
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
)
