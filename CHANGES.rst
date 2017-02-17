=========
CHANGELOG
=========

0.6: February 17th, 2017
========================

**NOTE**: This project is deprecated and no longer supported.

* Add, update and fix documentation.
* Code cleanup.
* Use static_finder even in DEBUG=False (bug 1054306)
* Allow files to be in django apps (bug 1054306)
* Make possible to define a custom static root
* Make possible to have STATIC_ROOT outside git repository
* Remove GitPython dependency, by using subprocess module to directly invoke git instead.
* Add contribute.json file.
* Call minify if minified file doesn't exist
* added inline_css() helper fixed some typo and pep8 invalidation in helper
* Update get_js_urls and get_css_urls to return absolute URLs.
* Add option to always include a timestamp in build_ids.
* Add -m option to ensure var names are mangled.
* add stylus support; fix sass support
* Make JINGO_MINIFY_USE_STATIC default consistent
* add sass css support
* Use mtime for build ID in dev for debugging.
* fix tests using bad path
* do not block on HTTP errors when fetching external JS/CSS
* allow for http/https urls to render without media prefix
* Add timestamp to URLs in debug mode.
* tell us the arguments of failed commands
* Make compress_assets exit non-zero on errors
* Let projects specify css media default in settings
* Add support for using staticfiles_ instead of ``MEDIA_URL``.
* Update YUICompressor to 2.4.7.
* Change setting from ``UGLIFYJS_BIN`` to ``UGLIFY_BIN``.
* Allow ``defer`` attribute on scripts.
* Keep copyright info in JS.
* Allow specifying default ``media`` attribute for CSS in settings.
* ``compress_assets`` has non-zero exit status on error.
* Raise an error instead of hanging on empty bundles.
* More useful output on error.
* Support URLs in bundles.
* Clean up README.rst so it parses as ReST.
* Add Travis-CI support.

.. _staticfiles: https://docs.djangoproject.com/en/dev/howto/static-files/


0.5
===

* Add support for UglifyJS_ and clean-css_.
* Support cache-busting images in CSS.
* Add --update-only option.
* Print out more info with --verbosity.
* Only minify changed files.
* Clean-up and refactor.


.. _UglifyJS: http://marijnhaverbeke.nl/uglifyjs
.. _clean-css: https://github.com/GoalSmashers/clean-css


0.4
===

* Add support for LESS_.

.. _LESS: http://lesscss.org/


0.3.2
=====

* Upgrade to YUICompressor 2.4.4.
