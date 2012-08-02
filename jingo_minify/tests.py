from django.conf import settings

import jingo
from mock import patch
from nose.tools import eq_


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

    expected ="\n".join(['<script src="%s?build=1"></script>'
                        % (settings.MEDIA_URL + j) for j in
                        settings.MINIFY_BUNDLES['js']['common']])

    eq_(s, expected)

    t = env.from_string("{{ js('common', debug=False) }}")
    s = t.render()

    eq_(s, '<script src="%s"></script>' %
           (settings.MEDIA_URL + "js/common-min.js?build=%s" % BUILD_ID_JS))


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
        'href="%s?build=1" />' % (settings.MEDIA_URL + j) for j in
         settings.MINIFY_BUNDLES['css']['common']])

    eq_(s, expected)

    t = env.from_string("{{ css('common', debug=False) }}")
    s = t.render()

    eq_(s,
        '<link rel="stylesheet" media="screen,projection,tv" href="%s" />'
        % (settings.MEDIA_URL + 'css/common-min.css?build=%s' % BUILD_ID_CSS))
