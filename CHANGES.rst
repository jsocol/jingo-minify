=========
CHANGELOG
=========

0.6
=====

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
