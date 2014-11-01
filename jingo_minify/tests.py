import os
import tempfile
from django.conf import settings
from django.test.utils import override_settings

import jingo
from mock import ANY, call, patch
from nose.tools import eq_

from .utils import get_media_root, get_media_url
from .management.commands.compress_assets import Command

try:
    from build import BUILD_ID_CSS, BUILD_ID_JS
except:
    BUILD_ID_CSS = BUILD_ID_JS = 'dev'


def setup():
    jingo.load_helpers()


@patch('jingo_minify.helpers.time.time')
@patch('jingo_minify.helpers.os.path.getmtime')
def test_js_helper(getmtime, time):
    """
    Given the js() tag if we return the assets that make up that bundle
    as defined in settings.MINIFY_BUNDLES.

    If we're not in debug mode, we just return a minified url
    """
    getmtime.return_value = 1
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

    eq_(s,
        '<script src="%sjs/common_protocol_less_url-min.js?build=%s">'
        '</script>' % (settings.STATIC_URL, BUILD_ID_JS))

    t = env.from_string("{{ js('common_bundle', debug=True) }}")
    s = t.render()

    eq_(s, '<script src="js/test.js?build=1"></script>\n'
           '<script src="http://example.com/test.js?build=1"></script>\n'
           '<script src="//example.com/test.js?build=1"></script>\n'
           '<script src="https://example.com/test.js?build=1"></script>')

    t = env.from_string("{{ js('common_bundle', debug=False) }}")
    s = t.render()

    eq_(s, '<script src="%sjs/common_bundle-min.js?build=%s"></script>'
           % (settings.STATIC_URL, BUILD_ID_JS))


@patch('jingo_minify.helpers.time.time')
@patch('jingo_minify.helpers.os.path.getmtime')
def test_css_helper(getmtime, time):
    """
    Given the css() tag if we return the assets that make up that bundle
    as defined in settings.MINIFY_BUNDLES.

    If we're not in debug mode, we just return a minified url
    """
    getmtime.return_value = 1
    time.return_value = 1
    env = jingo.env

    t = env.from_string("{{ css('common', debug=True) }}")
    s = t.render()

    expected = "\n".join(
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
@patch('jingo_minify.helpers.os.path.getmtime')
@override_settings(STATIC_ROOT='static',
                   MEDIA_ROOT='media',
                   STATIC_URL='http://example.com/static/',
                   MEDIA_URL='http://example.com/media/',
                   BUNDLES_DIR='bundled')
def test_bundles_dir(getmtime, time):
    getmtime.return_value = 1
    time.return_value = 1
    env = jingo.env

    t = env.from_string("{{ js('common', debug=False) }}")
    s = t.render()

    eq_(s, '<script src="%sbundled/js/common-min.js?build=%s"></script>' %
           (settings.STATIC_URL, BUILD_ID_JS))

    t = env.from_string("{{ css('common', debug=False) }}")
    s = t.render()

    eq_(s,
        '<link rel="stylesheet" media="screen,projection,tv" '
        'href="%sbundled/css/common-min.css?build=%s" />'
        % (settings.STATIC_URL, BUILD_ID_CSS))


def test_inline_css_helper():
    env = jingo.env
    t = env.from_string("{{ inline_css('common', debug=True) }}")
    s = t.render()

    eq_(s, '<style type="text/css" media="screen,projection,tv">'
           'body {\n    color: #999;\n}\n</style>')

    t = env.from_string("{{ inline_css('common', debug=False) }}")
    s = t.render()

    eq_(s, '<style type="text/css" media="screen,projection,tv">body'
           '{color:#999}</style>')


def test_inline_css_helper_multiple_files():
    env = jingo.env
    t = env.from_string("{{ inline_css('common_multi', debug=True) }}")
    s = t.render()

    eq_(s, '<style type="text/css" media="screen,projection,tv">body {\n    '
           'color: #999;\n}\n</style>\n<style type="text/css" media="screen,'
           'projection,tv">body {\n    color: #999;\n}\n</style>')

    t = env.from_string("{{ inline_css('common_multi', debug=False) }}")
    s = t.render()

    eq_(s, '<style type="text/css" media="screen,projection,tv">body{color:'
           '#999}\nmain{font-size:1em}\n</style>')


def test_inline_css_helper_external_url():
    env = jingo.env

    t = env.from_string("{{ inline_css('common_url', debug=True) }}")
    s = t.render()

    eq_(s, '<link rel="stylesheet" media="screen,projection,tv" '
           'href="http://example.com/test.css" />')

    t = env.from_string("{{ inline_css('common_url', debug=False) }}")
    s = t.render()

    eq_(s, '<style type="text/css" media="screen,projection,tv">'
        'body{color:#999}</style>')


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
@patch('jingo_minify.helpers.os.path.getmtime')
def test_css(getmtime, time):
    getmtime.return_value = 1
    time.return_value = 1
    env = jingo.env

    t = env.from_string("{{ css('common', debug=True) }}")
    s = t.render()

    expected = "\n".join(
        ['<link rel="stylesheet" media="screen,projection,tv" '
         'href="%s?build=1" />' % (settings.STATIC_URL + j)
         for j in settings.MINIFY_BUNDLES['css']['common']])

    eq_(s, expected)


@override_settings(STATIC_ROOT='static',
                   MEDIA_ROOT='media',
                   LESS_PREPROCESS=True,
                   LESS_BIN='lessc-bin',
                   SASS_BIN='sass-bin',
                   STYLUS_BIN='stylus-bin')
@patch('jingo_minify.helpers.time.time')
@patch('jingo_minify.helpers.os.path.getmtime')
@patch('jingo_minify.helpers.subprocess')
@patch('__builtin__.open', spec=True)
def test_compiled_css(open_mock, subprocess_mock, getmtime_mock, time_mock):
    jingo.env.from_string("{{ css('compiled', debug=True) }}").render()

    eq_(subprocess_mock.Popen.mock_calls,
        [call(['lessc-bin', 'static/css/less.less'], stdout=ANY),
         call(['sass-bin', 'static/css/sass.sass'], stdout=ANY),
         call(['sass-bin', 'static/css/scss.scss'], stdout=ANY)])

    subprocess_mock.call.assert_called_with(
        'stylus-bin --include-css --include '
        'static/css < static/css/stylus.styl > static/css/stylus.styl.css',
        shell=True)


@override_settings(STATIC_ROOT='static',
                   MEDIA_ROOT='media',
                   STATIC_URL='http://example.com/static/',
                   MEDIA_URL='http://example.com/media/')
@patch('jingo_minify.helpers.time.time')
@patch('jingo_minify.helpers.os.path.getmtime')
def test_js(getmtime, time):
    getmtime.return_value = 1
    time.return_value = 1
    env = jingo.env

    t = env.from_string("{{ js('common', debug=True) }}")
    s = t.render()

    expected = "\n".join(
        ['<script src="%s?build=1"></script>' % (settings.STATIC_URL + j)
         for j in settings.MINIFY_BUNDLES['js']['common']])

    eq_(s, expected)


@override_settings(STATIC_ROOT='static',
                   MEDIA_ROOT='media',
                   STATIC_URL='http://example.com/static/',
                   MEDIA_URL='http://example.com/media/')
def test_fix_urls():
    """Make sure relative URL's are fixed correctly"""
    command = Command()

    tmp = tempfile.mkstemp()[1]

    tmp_file = open(tmp, 'w')
    tmp_file.write('url(../img/test.png);')
    tmp_file.close()

    # Test files in same directory
    compressed = command._fix_urls(tmp,
        os.path.join(os.path.dirname(tmp), 'compiled'))
    compressed_file = open(compressed, 'r')
    eq_(compressed_file.read(), 'url(../img/test.png);')
    compressed_file.close()

    # Test files in different directory
    compressed = command._fix_urls(tmp,
        os.path.join(os.path.dirname(tmp), 'dir', 'compiled'))
    compressed_file = open(compressed, 'r')
    eq_(compressed_file.read(), 'url(../../img/test.png);')
    compressed_file.close()

    # Remove temporary files
    os.remove(compressed)
    os.remove(tmp)

    # Test data urls are unchanged
    data_url = ('url(data:image/gif;base64,R0lGODlhEAAQAMQAAORHHOVSKudfOulr'
                'SOp3WOyDZu6QdvCchPGolfO0o/XBs/fNwfjZ0frl3/zy7////wAAAAAAAA'
                'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5'
                'BAkAABAALAAAAAAQABAAAAVVICSOZGlCQAosJ6mu7fiyZeKqNKToQGDsM8'
                'hBADgUXoGAiqhSvp5QAnQKGIgUhwFUYLCVDFCrKUE1lBavAViFIDlTImbK'
                'C5Gm2hB0SlBCBMQiB0UjIQA7);')

    tmp = tempfile.mkstemp()[1]
    tmp_file = open(tmp, 'w')
    tmp_file.write(data_url)
    tmp_file.close()

    compressed = command._fix_urls(tmp,
        os.path.join(os.path.dirname(tmp), 'compiled'))
    compressed_file = open(compressed, 'r')
    eq_(compressed_file.read(), data_url)
    compressed_file.close()

    # Remove temporary files
    os.remove(compressed)
    os.remove(tmp)

    # Test absolute paths are unchanged
    content = ('url(http://example.com/image.gif); '
               'url(https://example.com/image.png);')
    tmp = tempfile.mkstemp()[1]
    tmp_file = open(tmp, 'w')
    tmp_file.write(content)
    tmp_file.close()

    compressed = command._fix_urls(tmp,
        os.path.join(os.path.dirname(tmp), 'compiled'))
    compressed_file = open(compressed, 'r')
    eq_(compressed_file.read(), content)
    compressed_file.close()

    # Remove temporary files
    os.remove(compressed)
    os.remove(tmp)

