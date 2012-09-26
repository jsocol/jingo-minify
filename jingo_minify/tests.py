from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings

import jingo
from mock import patch
from nose.tools import eq_

from jingo_minify.helpers import (css_urls, get_media_root, get_media_url,
                                  js_urls)

try:
    from build import BUILD_ID_CSS, BUILD_ID_JS
except:
    BUILD_ID_CSS = BUILD_ID_JS = 'dev'


def setup():
    jingo.load_helpers()


@patch('jingo_minify.helpers.time.time')
def test_js_helper(time):
    """
    Given the js() tag if we return the assets that make up that bundle
    as defined in settings.MINIFY_BUNDLES.

    If we're not in debug mode, we just return a minified url
    """
    time.return_value = 1
    env = jingo.env

    t = env.from_string("{{ js('common', debug=True) }}")
    s = t.render()

    expected = "\n".join(['<script src="%s?build=1"></script>'
                         % (settings.STATIC_URL + j) for j in
                         settings.MINIFY_BUNDLES['js']['common']])

    eq_(s, expected)

    t = env.from_string("{{ js('common', debug=False) }}")
    s = t.render()

    eq_(s, '<script src="%sjs/common-min.js?build=%s"></script>' %
           (settings.STATIC_URL, BUILD_ID_JS))

    t = env.from_string("{{ js('common_url', debug=True) }}")
    s = t.render()

    eq_(s, '<script src="%s"></script>' %
           "http://example.com/test.js?build=1")

    t = env.from_string("{{ js('common_url', debug=False) }}")
    s = t.render()

    eq_(s, '<script src="%sjs/common_url-min.js?build=%s"></script>' %
           (settings.STATIC_URL, BUILD_ID_JS))

    t = env.from_string("{{ js('common_protocol_less_url', debug=True) }}")
    s = t.render()

    eq_(s, '<script src="%s"></script>' %
           "//example.com/test.js?build=1")

    t = env.from_string("{{ js('common_protocol_less_url', debug=False) }}")
    s = t.render()

    eq_(s, '<script src="%sjs/common_protocol_less_url-min.js?build=%s">'
           '</script>' % (settings.STATIC_URL, BUILD_ID_JS))

    t = env.from_string("{{ js('common_bundle', debug=True) }}")
    s = t.render()

    eq_(s, '<script src="js/test.js?build=1"></script>\n'
           '<script src="http://example.com/test.js?build=1"></script>\n'
           '<script src="//example.com/test.js?build=1"></script>\n'
           '<script src="https://example.com/test.js?build=1"></script>')

    t = env.from_string("{{ js('common_bundle', debug=False) }}")
    s = t.render()

    eq_(s, '<script src="%sjs/common_bundle-min.js?build=%s"></script>' %
           (settings.STATIC_URL, BUILD_ID_JS))


@patch('jingo_minify.helpers.time.time')
def test_js_helper_fn(time):
    """
    Given the js_urls() function, check that it yields URLs with build IDs.
    """
    time.return_value = 1

    eq_(list(js_urls('common', debug=True)),
        ['%s?build=1' % j for j in
         settings.MINIFY_BUNDLES['js']['common']])

    eq_(list(js_urls('common_url', debug=False)),
        ['js/common_url-min.js?build=%s' % BUILD_ID_JS])


@patch('jingo_minify.helpers.time.time')
def test_css_helper(time):
    """
    Given the css() tag if we return the assets that make up that bundle
    as defined in settings.MINIFY_BUNDLES.

    If we're not in debug mode, we just return a minified url
    """
    time.return_value = 1
    env = jingo.env

    t = env.from_string("{{ css('common', debug=True) }}")
    s = t.render()

    expected ="\n".join(
        ['<link rel="stylesheet" media="screen,projection,tv" '
        'href="%s?build=1" />' % (settings.STATIC_URL + j)
         for j in settings.MINIFY_BUNDLES['css']['common']])

    eq_(s, expected)

    t = env.from_string("{{ css('common', debug=False) }}")
    s = t.render()

    eq_(s,
        '<link rel="stylesheet" media="screen,projection,tv" '
        'href="%scss/common-min.css?build=%s" />'
        % (settings.STATIC_URL, BUILD_ID_CSS))

    t = env.from_string("{{ css('common_url', debug=True) }}")
    s = t.render()

    eq_(s, '<link rel="stylesheet" media="screen,projection,tv" '
           'href="http://example.com/test.css?build=1" />')

    t = env.from_string("{{ css('common_url', debug=False) }}")
    s = t.render()

    eq_(s,
        '<link rel="stylesheet" media="screen,projection,tv" '
        'href="%scss/common_url-min.css?build=%s" />'
        % (settings.STATIC_URL, BUILD_ID_CSS))

    t = env.from_string("{{ css('common_protocol_less_url', debug=True) }}")
    s = t.render()

    eq_(s, '<link rel="stylesheet" media="screen,projection,tv" '
           'href="//example.com/test.css?build=1" />')

    t = env.from_string("{{ css('common_protocol_less_url', debug=False) }}")
    s = t.render()

    eq_(s,
        '<link rel="stylesheet" media="screen,projection,tv" '
        'href="%scss/common_protocol_less_url-min.css?build=%s" />'
        % (settings.STATIC_URL, BUILD_ID_CSS))

    t = env.from_string("{{ css('common_bundle', debug=True) }}")
    s = t.render()

    eq_(s, '<link rel="stylesheet" media="screen,projection,tv" '
           'href="css/test.css?build=1" />\n'
           '<link rel="stylesheet" media="screen,projection,tv" '
           'href="http://example.com/test.css?build=1" />\n'
           '<link rel="stylesheet" media="screen,projection,tv" '
           'href="//example.com/test.css?build=1" />\n'
           '<link rel="stylesheet" media="screen,projection,tv" '
           'href="https://example.com/test.css?build=1" />')

    t = env.from_string("{{ css('common_bundle', debug=False) }}")
    s = t.render()

    eq_(s, '<link rel="stylesheet" media="screen,projection,tv" '
           'href="%scss/common_bundle-min.css?build=%s" />' %
           (settings.STATIC_URL, BUILD_ID_CSS))


@patch('jingo_minify.helpers.time.time')
def test_css_helper_fn(time):
    """
    Given the css_urls() function, check that it yields URLs with build IDs.
    """
    time.return_value = 1

    eq_(list(css_urls('common', debug=True)),
        ['%s?build=1' % j
         for j in settings.MINIFY_BUNDLES['css']['common']])

    eq_(list(css_urls('common_bundle', debug=False)),
        ['css/common_bundle-min.css?build=%s' % BUILD_ID_CSS])


@override_settings(STATIC_ROOT='static',
                   MEDIA_ROOT='media',
                   STATIC_URL='http://example.com/static',
                   MEDIA_URL='http://example.com/media')
def test_no_override():
    """No override uses STATIC versions."""
    eq_(get_media_root(), 'static')
    eq_(get_media_url(), 'http://example.com/static')


@override_settings(JINGO_MINIFY_USE_STATIC=False,
                   STATIC_ROOT='static',
                   MEDIA_ROOT='media',
                   STATIC_URL='http://example.com/static',
                   MEDIA_URL='http://example.com/media')
def test_static_override():
    """Overriding to False uses MEDIA versions."""
    eq_(get_media_root(), 'media')
    eq_(get_media_url(), 'http://example.com/media')


@override_settings(STATIC_ROOT='static',
                   MEDIA_ROOT='media',
                   STATIC_URL='http://example.com/static/',
                   MEDIA_URL='http://example.com/media/')
@patch('jingo_minify.helpers.time.time')
def test_css(time):
    time.return_value = 1
    env = jingo.env

    t = env.from_string("{{ css('common', debug=True) }}")
    s = t.render()

    expected ="\n".join(
        ['<link rel="stylesheet" media="screen,projection,tv" '
         'href="%s?build=1" />' % (settings.STATIC_URL + j)
         for j in settings.MINIFY_BUNDLES['css']['common']])

    eq_(s, expected)


@override_settings(STATIC_ROOT='static',
                   MEDIA_ROOT='media',
                   STATIC_URL='http://example.com/static/',
                   MEDIA_URL='http://example.com/media/')
@patch('jingo_minify.helpers.time.time')
def test_js(time):
    time.return_value = 1
    env = jingo.env

    t = env.from_string("{{ js('common', debug=True) }}")
    s = t.render()

    expected = "\n".join(
        ['<script src="%s?build=1"></script>' % (settings.STATIC_URL + j)
         for j in settings.MINIFY_BUNDLES['js']['common']])

    eq_(s, expected)
