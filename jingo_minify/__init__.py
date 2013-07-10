import os
import warnings

def check_css():
    try:
        from django.conf import settings
    except ImportError:
        return []

    w = []

    less_found = False
    sass_found = False
    stylus_found = False
    for bundle, csses in settings.MINIFY_BUNDLES['css'].iteritems():
        for item in csses:
            if item.endswith('.less'):
                less_found = True
            elif item.endswith('.sass'):
                sass_found = True
            elif item.endswith('.scss'):
                sass_found = True
            elif item.endswith('.styl'):
                stylus_found = True

    valid_less = (getattr(settings, 'LESS_BIN', False) and
                  getattr(settings, "LESS_PREPROCESS", False))
    valid_sass = getattr(settings, 'SASS_BIN', False)
    valid_stylus = getattr(settings, 'STYLUS_BIN', False)

    if less_found and not valid_less:
        w.append('LESS_BIN not found or LESS_PREPROCESS is '
                 'False/undefined but less files are being used!')

    if sass_found and not valid_sass:
        w.append('SASS_BIN not found but sass files are being used!')

    if stylus_found and not valid_stylus:
        w.append('STYLUS_BIN not found but stylus files are being used!')

    return w

for msg in check_css():
    warnings.warn(msg)

VERSION = (0, 6, 0)
__version__ = '.'.join((str(x) for x in VERSION))
