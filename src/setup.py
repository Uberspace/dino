from setuptools import find_packages, setup

setup(
    name='dino',
    version='0.1',
    python_requires='>=3.6',
    description='Admin interface for PowerDNS.',
    author='uberspace.de',
    author_email='hallo@uberspace.de',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    keywords='dns powerdns pdns admin administration',
    install_requires=[
        'Django==2.2b1',
        'dj-database-url==0.5.*',
        'requests',  # should be installed with python-powerdns ... ?
        'python-powerdns@https://github.com/vente-privee/python-powerdns/archive/1c61c574399e3e486a6e0b9d1e3d0521b2fa00a0.zip',
        'django-allauth==0.38.*',
        'rules==2.0.*',
        'whitenoise==4.1.*',
    ],
    extras_require={
        'dev': [
            'isort',
            'pylama',
            'ipython',
            'django-extensions',
        ],
        'test': [
            'pytest!=4.2.0,>=3.6',  # pytest-django version requirement
            'pytest-cov',
            'pytest-django',
            'pytest-mock',
            'pytest-lazy-fixture==0.5.*',
        ],
        'doc': [
            'sphinx',
            'sphinx_rtd_theme',
            'sphinx-autobuild',
        ],
    },
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
)
