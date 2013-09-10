import os

from django.conf import settings
from django.contrib.staticfiles.finders import find as static_finder


def get_media_root():
    """Return STATIC_ROOT or MEDIA_ROOT depending on JINGO_MINIFY_USE_STATIC.

    This allows projects using Django 1.4 to continue using the old
    ways, but projects using Django 1.4 to use the new ways.

    """
    if getattr(settings, 'JINGO_MINIFY_USE_STATIC', True):
        return settings.STATIC_ROOT
    return settings.MEDIA_ROOT


def get_media_url():
    """Return STATIC_URL or MEDIA_URL depending on JINGO_MINIFY_USE_STATIC.

    Allows projects using Django 1.4 to continue using the old ways
    but projects using Django 1.4 to use the new ways.

    """
    if getattr(settings, 'JINGO_MINIFY_USE_STATIC', True):
        return settings.STATIC_URL
    return settings.MEDIA_URL


def get_path(path):
    """Get a system path for a given file.

    This properly handles storing files in `project/app/static`, and any other
    location that Django's static files system supports.

    ``path`` should be relative to ``STATIC_ROOT``.

    """
    debug = getattr(settings, 'DEBUG', False)
    static = getattr(settings, 'JINGO_MINIFY_USE_STATIC', True)

    full_path = os.path.join(get_media_root(), path)

    if debug and static:
        found_path = static_finder(path)
        # If the path is not found by Django's static finder (like we are
        # trying to get an output path), it returns None, so fall back.
        if found_path is not None:
            full_path = found_path

    return full_path
