import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-perimeter',
    version='0.7.1',
    packages=['perimeter', 'perimeter.tests', 'perimeter.management.commands'],
    include_package_data=True,
    license='BSD License',
    description='Site-wide perimeter access control for Django projects.',
    long_description=README,
    url='https://github.com/yunojuno/django-perimeter',
    author='Hugo Rodger-Brown',
    author_email='hugo@yunojuno.com',
    install_requires=[
        'Django>=1.8',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
