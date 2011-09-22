import hashlib
from optparse import make_option
import os
import re
import time
from subprocess import call, PIPE

from django.conf import settings
from django.core.management.base import BaseCommand

import git


path = lambda *a: os.path.join(settings.MEDIA_ROOT, *a)


class Command(BaseCommand):  # pragma: no cover
    help = ("Compresses css and js assets defined in settings.MINIFY_BUNDLES")
    option_list = BaseCommand.option_list + (
        make_option('-u', '--update-only', action='store_true',
                    dest='do_update_only', help='Updates the hash only'),
    )
    requires_model_validation = False
    do_update_only = False

    checked_repos = {}
    checked_hash = {}

    def update_hashes(self, update=False, bundle_hashes={}):
        def gitid(path):
            id = (git.repo.Repo(os.path.join(settings.ROOT, path))
                     .log('-1')[0].id_abbrev)
            if update:
                # Adds a time based hash on to the build id.
                return '%s-%s' % (id, hex(int(time.time()))[2:])
            return id

        build_id_file = os.path.realpath(os.path.join(settings.ROOT,
                                                      'build.py'))
        with open(build_id_file, 'w') as f:
            f.write('BUILD_ID_CSS = "%s"' % gitid('media/css'))
            f.write("\n")
            f.write('BUILD_ID_JS = "%s"' % gitid('media/js'))
            f.write("\n")
            f.write('BUILD_ID_IMG = "%s"' % gitid('media/img'))
            f.write("\n")
            f.write('BUNDLE_HASHES = %s' % bundle_hashes)
            f.write("\n")

    def handle(self, **options):
        if options.get('do_update_only', False):
            self.update_hashes(update=True)
            return

        jar_path = (os.path.dirname(__file__), '..', '..', 'bin',
                'yuicompressor-2.4.4.jar')
        path_to_jar = os.path.realpath(os.path.join(*jar_path))

        v = ''
        if 'verbosity' in options and options['verbosity'] == '2':
            v = '-v'

        bundle_hashes = {}

        cachebust_imgs = getattr(settings, 'CACHEBUST_IMGS', False)
        if not cachebust_imgs:
            print "To turn on cache busting, use settings.CACHEBUST_IMGS"

        for ftype, bundle in settings.MINIFY_BUNDLES.iteritems():
            for name, files in bundle.iteritems():
                # Compile LESS files
                files_all = []
                for fn in files:
                    if fn.endswith('.less'):
                        fp = path(fn.lstrip('/'))
                        call('%s %s %s.css' % (settings.LESS_BIN, fp, fp),
                             shell=True)
                        # Outputs a *.less.css file.
                        files_all.append('%s.css' % fn)
                    else:
                        files_all.append(fn)

                concatted_file = path(ftype, '%s-all.%s' % (name, ftype,))
                compressed_file = path(ftype, '%s-min.%s' % (name, ftype,))
                real_files = [path(f.lstrip('/')) for f in files_all]

                file_path = os.path.join(settings.ROOT, concatted_file)

                # Concats the files.
                call("cat %s > %s" % (' '.join(real_files), concatted_file),
                     shell=True)

                # Cache bust individual images in the CSS
                if cachebust_imgs and ftype == "css":
                    css_content = ''
                    with open(concatted_file, 'r') as css_in:
                        css_content = css_in.read()

                    parse = lambda url: self.cachebust(url, concatted_file)
                    css_parsed = re.sub('url\(([^)]*?)\)', parse, css_content)

                    bundle_hash = hashlib.md5(css_parsed).hexdigest()[0:7]
                    bundle_hashes["%s:%s" % (ftype, name)] = bundle_hash
                    with open(concatted_file, 'w') as css_out:
                        css_out.write(css_parsed)
                    print "Cache busted images in %s" % file_path

                # Compresses the concatenation.
                if ftype == 'js' and hasattr(settings, 'UGLIFY_BIN'):
                    print "Minifying %s (using UglifyJS)" % concatted_file
                    call("%s %s -nc -o %s %s" % (settings.UGLIFY_BIN, v,
                            compressed_file, concatted_file),
                         shell=True, stdout=PIPE)
                elif ftype == 'css' and hasattr(settings, 'CLEANCSS_BIN'):
                    print "Minifying %s (using clean-css)" % concatted_file
                    call("%s -o %s %s" % (settings.CLEANCSS_BIN,
                            compressed_file, concatted_file),
                         shell=True, stdout=PIPE)
                else:
                    print "Minifying %s (using YUICompressor)" % concatted_file
                    call("%s -jar %s %s %s -o %s" % (settings.JAVA_BIN,
                            path_to_jar, v, concatted_file, compressed_file),
                         shell=True, stdout=PIPE)

        self.update_hashes(bundle_hashes=bundle_hashes)

    def get_repo(self, file_path):
        folder = os.path.dirname(file_path)
        repo = self.checked_repos[folder] if folder in self.checked_repos else git.repo.Repo(file_path)
        self.checked_repos[folder] = repo
        return repo

    def file_hash(self, url):
        if url in self.checked_hash:
            return self.checked_hash[url]

        file_hash = ""
        try:
            with open(url) as f:
                file_hash = hashlib.md5(f.read()).hexdigest()[0:7]
        except IOError:
            print " - Couldn't find file %s" % full_url

        self.checked_hash[url] = file_hash
        return file_hash

    def cachebust(self, img, parent):
        # We get a structural regex object back, hence the "group()"
        url = img.group(1).strip('"\'')
        if url.startswith('data:') or url.startswith('http'):
            return "url(%s)" % url

        url = url.split('?')[0]
        full_url = os.path.join(settings.ROOT, os.path.dirname(parent),
                                url)

        return "url(%s?%s)" % (url, self.file_hash(full_url))

