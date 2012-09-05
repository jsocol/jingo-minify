import os
import subprocess
import time

from django.conf import settings

import jinja2
from jingo import register, env


try:
    from build import BUILD_ID_CSS, BUILD_ID_JS, BUILD_ID_IMG, BUNDLE_HASHES
except ImportError:
    BUILD_ID_CSS = BUILD_ID_JS = BUILD_ID_IMG = 'dev'
    BUNDLE_HASHES = {}


def get_media_root():
    """Return STATIC_ROOT or MEDIA_ROOT depending on JINGO_MINIFY_USE_STATIC.

    This allows projects using Django 1.4 to continue using the old
    ways, but projects using Django 1.4 to use the new ways.

    """
    if getattr(settings, 'JINGO_MINIFY_USE_STATIC', False):
        return settings.STATIC_ROOT
    return settings.MEDIA_ROOT


def get_media_url():
    """Return STATIC_URL or MEDIA_URL depending on JINGO_MINIFY_USE_STATIC.

    Allows projects using Django 1.4 to continue using the old ways
    but projects using Django 1.4 to use the new ways.

    """
    if getattr(settings, 'JINGO_MINIFY_USE_STATIC', False):
        return settings.STATIC_URL
    return settings.MEDIA_URL


path = lambda *a: os.path.join(get_media_root(), *a)


def _get_item_path(item):
    """
    Determine whether to return a relative path or a URL.
    """
    if item.startswith(('//', 'http', 'https')):
        return item
    return get_media_url() + item


def _build_html(items, wrapping):
    """
    Wrap `items` in wrapping.
    """
    return jinja2.Markup('\n'.join((wrapping % (_get_item_path(item))
                                   for item in items)))


@register.function
def js(bundle, debug=settings.TEMPLATE_DEBUG, defer=False, async=False):
    """
    If we are in debug mode, just output a single script tag for each js file.
    If we are not in debug mode, return a script that points at bundle-min.js.
    """
    attrs = []

    if debug:
        # Add timestamp to avoid caching.
        items = ['%s?build=%s' % (item, int(time.time())) for item in
                 settings.MINIFY_BUNDLES['js'][bundle]]
    else:
        build_id = BUILD_ID_JS
        bundle_full = "js:%s" % bundle
        if bundle_full in BUNDLE_HASHES:
            build_id = BUNDLE_HASHES[bundle_full]
        items = ('js/%s-min.js?build=%s' % (bundle, build_id,),)

    attrs.append('src="%s"')

    if defer:
        attrs.append('defer')

    if async:
        attrs.append('async')

    string = '<script %s></script>' % ' '.join(attrs)
    return _build_html(items, string)


@register.function
def css(bundle, media=False, debug=settings.TEMPLATE_DEBUG):
    """
    If we are in debug mode, just output a single script tag for each css file.
    If we are not in debug mode, return a script that points at bundle-min.css.
    """
    if not media:
        media = getattr(settings, 'CSS_MEDIA_DEFAULT', "screen,projection,tv")

    if debug:
        items = []
        for item in settings.MINIFY_BUNDLES['css'][bundle]:
            if (item.endswith('.less') and
                getattr(settings, 'LESS_PREPROCESS', False)):
                build_less(item)
                items.append('%s.css' % item)
            else:
                items.append(item)

        # Add timestamp to avoid caching.
        items = ['%s?build=%s' % (item, int(time.time())) for item in items]
    else:
        build_id = BUILD_ID_CSS
        bundle_full = "css:%s" % bundle
        if bundle_full in BUNDLE_HASHES:
            build_id = BUNDLE_HASHES[bundle_full]

        items = ('css/%s-min.css?build=%s' % (bundle, build_id,),)

    return _build_html(items,
            '<link rel="stylesheet" media="%s" href="%%s" />' % media)

def build_less(item):
    path_css = path('%s.css' % item)
    path_less = path(item)

    updated_less = os.path.getmtime(path(item))
    updated_css = 0  # If the file doesn't exist, force a refresh.
    if os.path.exists(path_css):
        updated_css = os.path.getmtime(path_css)

    # Is the uncompiled version newer?  Then recompile!
    if updated_less > updated_css:
        with open(path_css, 'w') as output:
            subprocess.Popen([settings.LESS_BIN, path_less],
                             stdout=output)

def build_ids(request):
    """A context processor for injecting the css/js build ids."""
    return {'BUILD_ID_CSS': BUILD_ID_CSS, 'BUILD_ID_JS': BUILD_ID_JS,
            'BUILD_ID_IMG': BUILD_ID_IMG}

