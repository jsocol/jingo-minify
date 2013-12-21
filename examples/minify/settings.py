import os

TEST_RUNNER = 'django_nose.runner.NoseTestSuiteRunner'

ROOT = os.path.dirname(os.path.abspath(__file__))
path = lambda *a: os.path.join(ROOT, *a)

MEDIA_ROOT = '/media'
MEDIA_URL = ''
STATIC_ROOT = path('static')
STATIC_URL = ''

DATABASES = {
    'default': {
        'NAME': 'test.db',
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

INSTALLED_APPS = (
    'jingo_minify',
    'django_nose',
    'minify',
)

MINIFY_BUNDLES = {
    'css': {
        'common': ['css/test.css'],
        'common_multi': ['css/test.css', 'css/test2.css'],
        'common_url': ['http://example.com/test.css'],
        'common_protocol_less_url': ['//example.com/test.css'],
        'common_bundle': ['css/test.css', 'http://example.com/test.css',
                          '//example.com/test.css',
                          'https://example.com/test.css'],
        'compiled': ['css/plain.css',
                     'css/less.less',
                     'css/sass.sass',
                     'css/scss.scss',
                     'css/stylus.styl']
    },
    'js': {
        'common': ['js/test.js'],
        'common_url': ['http://example.com/test.js'],
        'common_protocol_less_url': ['//example.com/test.js'],
        'common_bundle': ['js/test.js', 'http://example.com/test.js',
                          '//example.com/test.js',
                          'https://example.com/test.js'],
    },
}

LESS_PREPROCESS = True
LESS_BIN = '/usr/bin/lessc'

SASS_PREPROCESS = True
SASS_BIN = '/usr/bin/sass'
