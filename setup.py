from setuptools import setup, find_packages

import jingo_minify

setup(
    name='jingo_minify',
    version=jingo_minify.__version__,
    description='A Django app that will concat and minify JS and CSS.',
    long_description=open('README.rst').read(),
    author='Dave Dash, James Socol',
    author_email='dd@mozilla.com, james@mozilla.com',
    url='http://github.com/jsocol/jingo-minify',
    license='BSD',
    packages=find_packages(exclude=['examples.*']),
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Environment :: Web Environment :: Mozilla',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
