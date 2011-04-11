import os
import subprocess

from django.conf import settings

from jinja2 import Markup
from jingo import register, env


try:
    from build import BUILD_ID_CSS, BUILD_ID_JS, BUILD_ID_IMG
except ImportError:
    BUILD_ID_CSS = BUILD_ID_JS = BUILD_ID_IMG = 'dev'

path = lambda *a: os.path.join(settings.MEDIA_ROOT, *a)

def _build_html(items, wrapping):
    """
    Wrap `items` in wrapping.
    """
    return Markup("\n".join((wrapping % (settings.MEDIA_URL + item)
                            for item in items)))

@register.function
def js(bundle, debug=settings.TEMPLATE_DEBUG):
    """
    If we are in debug mode, just output a single script tag for each js file.
    If we are not in debug mode, return a script that points at bundle-min.js.
    """
    if debug:
        items = settings.MINIFY_BUNDLES['js'][bundle]
    else:
        items = ("js/%s-min.js?build=%s" % (bundle, BUILD_ID_JS,),)

    return _build_html(items, """<script src="%s"></script>""")


@register.function
def css(bundle, media="screen,projection,tv", debug=settings.TEMPLATE_DEBUG):
    """
    If we are in debug mode, just output a single script tag for each css file.
    If we are not in debug mode, return a script that points at bundle-min.css.
    """
    if debug:
        items = []
        for item in settings.MINIFY_BUNDLES['css'][bundle]:
            if item.endswith('.less') and settings.LESS_PREPROCESS:
                build_less(item)
                items.append('%s.css' % item)
            else:
                items.append(item)
    else:
        items = ("css/%s-min.css?build=%s" % (bundle, BUILD_ID_CSS,),)

    return _build_html(items,
            """<link rel="stylesheet" media="%s" href="%%s" />""" % media)

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
