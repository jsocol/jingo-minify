from setuptools import setup

setup(
    name='jingo_minify',
    version='0.1',
    description='A Django app that will concat and minify JS and CSS.',
    author='Dave Dash, James Socol',
    author_email='dd@mozilla.com, james@mozilla.com',
    url='http://github.com/jsocol/jingo_minify',
    license='BSD',
    packages=['jingo_minify'],
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
