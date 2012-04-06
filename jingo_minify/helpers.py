import os
import subprocess

from django.conf import settings

import jinja2
from jingo import register, env


try:
    from build import BUILD_ID_CSS, BUILD_ID_JS, BUILD_ID_IMG, BUNDLE_HASHES
except ImportError:
    BUILD_ID_CSS = BUILD_ID_JS = BUILD_ID_IMG = 'dev'
    BUNDLE_HASHES = {}


# Use STATIC_* if set or fall back to MEDIA_*.
STATIC_OR_MEDIA_ROOT = getattr(settings, 'STATIC_ROOT', settings.MEDIA_ROOT)
STATIC_OR_MEDIA_URL = getattr(settings, 'STATIC_URL', settings.MEDIA_URL)

def _build_html(items, wrapping):
    """
    Wrap `items` in wrapping.
    """
    return jinja2.Markup("\n".join((wrapping % item for item in items)))

@register.function
def js(bundle, debug=settings.TEMPLATE_DEBUG, defer=False, async=False):
    """
    If we are in debug mode, just output a single script tag for each js file.
    If we are not in debug mode, return a script that points at bundle-min.js.
    """
    attrs = []

    if debug:
        items = settings.MINIFY_BUNDLES['js'][bundle]
        items = [STATIC_OR_MEDIA_URL + i for i in items]
    else:
        build_id = BUILD_ID_JS
        bundle_full = "js:%s" % bundle
        if bundle_full in BUNDLE_HASHES:
            build_id = BUNDLE_HASHES[bundle_full]
        items = ('%s/js/%s-min.js?build=%s' %
                    (settings.MEDIA_URL, bundle, build_id,),)

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
        items = [STATIC_OR_MEDIA_URL + i for i in items]
    else:
        build_id = BUILD_ID_CSS
        bundle_full = "css:%s" % bundle
        if bundle_full in BUNDLE_HASHES:
            build_id = BUNDLE_HASHES[bundle_full]

        items = ('%s/css/%s-min.css?build=%s' %
                    (settings.MEDIA_URL, bundle, build_id,),)

    return _build_html(items,
            '<link rel="stylesheet" media="%s" href="%%s" />' % media)

def build_less(item):
    path_css = os.path.join(settings.MEDIA_ROOT, '%s.css' % item)
    path_less = os.path.join(settings.MEDIA_ROOT, item)

    updated_less = os.path.getmtime(path_less)
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

