from setuptools import setup, find_packages

import jingo_minify

setup(
    name='jingo_minify',
    version=jingo_minify.__version__,
    description='DEPRECATED - A Django app that will concat and minify JS and CSS.',
    long_description=open('README.rst').read(),
    author='Dave Dash, James Socol',
    author_email='dd@mozilla.com, james@mozilla.com',
    url='http://github.com/jsocol/jingo-minify',
    license='BSD',
    packages=find_packages(exclude=['examples.*']),
    include_package_data=True,
    install_requires=[
        'jingo>=0.8',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Environment :: Web Environment :: Mozilla',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
