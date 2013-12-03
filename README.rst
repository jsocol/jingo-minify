============
Jingo Minify
============

Jingo Minify is an CSS/JS bundler and minifier for use with Jingo_, a connector
to use Jinja2_ templates with Django_.

.. image:: https://api.travis-ci.org/jsocol/jingo-minify.png


Installing Jingo Minify
=======================


Requirements
------------

* **Django 1.4**

* **Jingo and Jinja2**. Jingo Minify is not designed for Django templates.

One of the following:

* **Java**. If you want to use YUI Compressor.

* **NodeJS**. If you want to use UglifyJS_ and clean-css_.

Optionally:

* **less**. Jingo Minify supports less_, if you have ``lessc`` available.
* **sass**. Jingo Minify supports sass_, if you have ``sass`` available.
* **stylus**. Jingo Minify supports stylus_, if you have ``stylus`` available.


Installation
------------

Configure the following settings::

    # Jingo Minify uses the YUICompressor internally, so needs Java.
    JAVA_BIN = '/path/to/java'

    # If you want to use less, set this:
    LESS_BIN = '/path/to/lessc' # Probably just 'lessc'

    # If you want to use sass, set this:
    SASS_BIN = '/path/to/sass'

    # If you want to use node-based minifiers, set these:
    UGLIFY_BIN = '/path/to/uglifyjs' # Probably just 'uglify'
    CLEANCSS_BIN = '/path/to/cleancss' # Probably just 'cleancss'

    # Add jingo_minify to INSTALLED_APPS
    INSTALLED_APPS = (
        # ...
        'jingo_minify',
        # ...
    )

    # This is the important part.
    MINIFY_BUNDLES = {
        'css': {},
        'js': {},
    }


Note: If you're using Django 1.4, but want to use MEDIA_ROOT and MEDIA_URL
for static assets instead of conventional Django 1.4 STATIC_ROOT and
STATIC_URL, you should also set::

    JINGO_MINIFY_USE_STATIC = False


Configuring
===========

Jingo Minify deals with *bundles*, which lets you organize your code into
multiple files but combine them into very few groups for your users to
download.

Bundles are set up in the ``MINIFY_BUNDLES`` setting. For example::

    MINIFY_BUNDLES = {
        'css': {
            'common': (
                'css/reset.css',
                'css/layout.css',
            ),
        },
        'js': {
            'common': (
                'js/lib/jquery.js',
                'js/common.js',
            ),
        },
    }

This creates one CSS bundle and one JS bundle, both called ``common``. The file
paths are relative to the ``MEDIA_ROOT`` setting.

You can create any number or combination of CSS and JS bundles, and include any
number of files in each, but **do not create empty bundles**.

Using Bundled Files
-------------------

For development, you probably don't want to rebundle the files all the time.
Just set

::

    TEMPLATE_DEBUG = True

in your settings, and Jingo Minify will automatically use the uncompressed
files. Set ``TEMPLATE_DEBUG`` to ``False`` to use the bundled versions.

In Templates
============

To include a bundle in a template, use either the ``css`` or ``js`` functions.
For example::

    {# My Jinja2 Template #}
    <html>
    <head>
      <title>My Page</title>
      {{ css('common') }}
    </head>
    <body>
      <h1>My page</h1>
      {{ js('common') }}
    </body>
    </html>

This will include the code (``<link>`` and ``<script>`` tags) to include the
bundles on the page. It will generate the HTML for either the individual files
or the bundled files based on ``TEMPLATE_DEBUG``.


Media Types
-----------

The ``css()`` helper will, by default, generate ``<link>`` tags with a
``media`` attribute set to ``screen,projection,tv``. You can override this by
passing an optional second parameter to the ``css()`` helper, e.g.::

    {{ css('print-bundle', 'print') }}

This would create a ``<link>`` tag with ``media="print"``.


Bundling and Minifying
======================

To bundle and minify your CSS and JS, run the management command::

    ./manage.py compress_assets

This will create two files per bundle in your ``media`` directory, one that
looks like ``bundle-all.js`` (or ``.css``) and one that looks like
``bundle-min.js``. Only the ``*-min.*`` version will be used. It also creates a
file called ``build.py`` along side ``manage.py`` that contains unique IDs
based on the SHA of the current git checkout.


Minifier Options
----------------

You can choose between YUICompressor (Java) or UglifyJS/clean-css (node) for
minifying.  You don't have to do anything to get YUICompressor working.

If you want to use the node counterparts, just add ``UGLIFY_BIN`` and
``CLEANCSS_BIN`` (set to the correct paths, of course) to your ``settings.py``.
You can see the actual syntax if you look at the Installation section of this
README.


Cache Busting Individual Images
==============================

Depending on your CDN, you may need to cache-bust assets referenced in the CSS.
To do this, add the following to your settings::

    CACHEBUST_IMGS = True

It will go through your CSS, and find any reference to local resources.  It
will append the short id for the commit that most recently modified the
resource, so that it only cache busts resources that are actually modified.

The list of images that couldn't be found can be displayed by running the
command with `--verbosity=2` (or `-v2`).

::

    manage.py compress_assets -v2

.. note::
    This is off by default.  It does a lot of I/O, so be careful if you have
    large amounts of massive images.  Additionally, it uses a hash of the file.
    This isn't 100% collision proof, but it should be more than good enough.


Using LESS
==========

If you want to use less_ files and have ``LESS_BIN`` defined, LESS is
supported automatically in a few ways.

* To use a LESS file, simply include a file in a CSS bundle that ends with
  ``.less``.

* For development, if you want to use the LESS JavaScript runtime compiler,
  you'll have to figure out how to include it in your project.

* If you want to compile LESS on the server, even in development, add a
  setting: ``LESS_PREPROCESS = True``. Your LESS files will be recompiled on
  every request.

* In production, LESS files are automatically compiled before being bundled
  with the rest of the CSS.


Using SASS or Stylus
====================

If you want to use sass_ or stylus_ files, you must define ```SASS_BIN`` or
``STYLUS_BIN``, respectively.

* To use a SASS or Stylus file, simply include a file in a CSS bundle that
  ends with ``.sass`` or ``.scss`` (SASS) or ``.styl`` (Stylus).

* Your SASS/Stylus files, if changed, will be recompiled on every request -
  even in development.

* In production, Sass/Stylus files are automatically compiled before being
  bundled with the rest of the CSS.


Running tests
=============

To run the tests::

    $ python run_tests.py


.. _Jingo: https://github.com/jbalogh/jingo
.. _Jinja2: http://jinja.pocoo.org/docs/
.. _Django: https://www.djangoproject.com/
.. _less: http://lesscss.org/
.. _sass: http://sass-lang.com/
.. _stylus: http://learnboost.github.com/stylus/
.. _UglifyJS: https://github.com/mishoo/UglifyJS
.. _clean-css: https://github.com/GoalSmashers/clean-css
