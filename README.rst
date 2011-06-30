============
Jingo Minify
============

Jingo Minify is an CSS/JS bundler and minifier for use with Jingo_, a connector
to use Jinja2_ templates with Django_.


Installing Jingo Minify
=======================


Requirements
------------

* **Java**. Jingo Minify uses the YUICompressor internally.
* **Jingo and Jinja2**. Jingo Minify is not designed for Django templates.

Optionally:

* **less**. Jingo Minify supports less_, if you have ``lessc`` available.


Installation
------------

Configure the following settings::

    # Jingo Minify uses the YUICompressor internally, so needs Java.
    JAVA_BIN = '/path/to/java'

    # If you want to use less, set this:
    LESS_BIN = '/path/to/lessc'

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


Using LESS
==========

If you want to use less_ files and have ``LESS_BIN`` defined, less is supported
automatically in a few ways.

* To use a less file, simply include a file in a CSS bundle that ends with
  ``.less``.

* For development, if you want to use the less JavaScript runtime compiler,
  you'll have to figure out how to include it in your project.

* If you want to compile less on the server, even in development, add a
  setting: ``LESS_PREPROCESS = True``. Your less files will be recompiled on
  every request.

* In production, less files are automatically compiled before being bundled
  with the rest of the CSS.


.. _Jingo: https://github.com/jbalogh/jingo
.. _Jinja2: http://jinja.pocoo.org/docs/
.. _Django: https://www.djangoproject.com/
.. _less: http://lesscss.org/
