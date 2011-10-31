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

    checked_hash = {}
    bundle_hashes = {}

    missing_files = 0
    minify_skipped = 0

    def update_hashes(self, update=False):
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
            f.write('BUNDLE_HASHES = %s' % self.bundle_hashes)
            f.write("\n")

    def handle(self, **options):
        if options.get('do_update_only', False):
            self.update_hashes(update=True)
            return

        jar_path = (os.path.dirname(__file__), '..', '..', 'bin',
                'yuicompressor-2.4.4.jar')
        self.path_to_jar = os.path.realpath(os.path.join(*jar_path))

        self.v = '-v' if options.get('verbosity', False) == '2' else ''

        cachebust_imgs = getattr(settings, 'CACHEBUST_IMGS', False)
        if not cachebust_imgs:
            print "To turn on cache busting, use settings.CACHEBUST_IMGS"

        # This will loop through every bundle, and do the following:
        # - Concat all files into one
        # - Cache bust all images in CSS files
        # - Minify the concatted files

        for ftype, bundle in settings.MINIFY_BUNDLES.iteritems():
            for name, files in bundle.iteritems():
                # Set the paths to the files
                concatted_file = path(ftype, '%s-all.%s' % (name, ftype,))
                compressed_file = path(ftype, '%s-min.%s' % (name, ftype,))
                files_all = [self._preprocess_file(fn) for fn in files]

                # Concat all the files.
                tmp_concatted = '%s.tmp' % concatted_file
                call("cat %s > %s" % (' '.join(files_all), tmp_concatted),
                     shell=True)

                # Cache bust individual images in the CSS
                if cachebust_imgs and ftype == "css":
                    bundle_hash = self._cachebust(tmp_concatted, name)
                    self.bundle_hashes["%s:%s" % (ftype, name)] = bundle_hash

                # Compresses the concatenations.
                is_changed = self._is_changed(concatted_file)
                self._clean_tmp(concatted_file)
                if is_changed:
                    self._minify(ftype, concatted_file, compressed_file)
                elif self.v:
                    print "File unchanged, skipping minification of %s" % (
                            concatted_file)
                else:
                    self.minify_skipped += 1

        # Write out the hashes
        self.update_hashes()

        if not self.v and self.minify_skipped:
            print "Unchanged files skipped for minification: %s" % (
                    self.minify_skipped)

    def _preprocess_file(self, filename):
        """Preprocess files and return new filenames."""
        if filename.endswith('.less'):
            fp = path(filename.lstrip('/'))
            call('%s %s %s.css' % (settings.LESS_BIN, fp, fp),
                 shell=True, stdout=PIPE)
            filename = '%s.css' % filename
        return path(filename.lstrip('/'))

    def _is_changed(self, concatted_file):
        """Check if the file has been changed."""
        tmp_concatted = '%s.tmp' % concatted_file
        if (os.path.exists(concatted_file) and
            os.path.getsize(concatted_file) == os.path.getsize(tmp_concatted)):
            orig_hash = self._file_hash(concatted_file)
            temp_hash = self._file_hash(tmp_concatted)
            return orig_hash != temp_hash
        return True  # Different filesize, so it was definitely changed

    def _clean_tmp(self, concatted_file):
        """Replace the old file with the temp file."""
        tmp_concatted = '%s.tmp' % concatted_file
        if os.path.exists(concatted_file):
            os.remove(concatted_file)
        os.rename(tmp_concatted, concatted_file)

    def _cachebust(self, css_file, bundle_name):
        """Cache bust images.  Return a new bundle hash."""
        print "Cache busting images in %s" % re.sub('.tmp$', '', css_file)

        css_content = ''
        with open(css_file, 'r') as css_in:
            css_content = css_in.read()

        parse = lambda url: self._cachebust_regex(url, css_file)
        css_parsed = re.sub('url\(([^)]*?)\)', parse, css_content)

        with open(css_file, 'w') as css_out:
            css_out.write(css_parsed)

        # Return bundle hash for cachebusting JS/CSS files.
        file_hash = hashlib.md5(css_parsed).hexdigest()[0:7]
        self.checked_hash[css_file] = file_hash

        if not self.v and self.missing_files:
           print " - Error finding %s images (-v2 for info)" % (
                   self.missing_files,)
           self.missing_files = 0

        return file_hash

    def _minify(self, ftype, file_in, file_out):
        """Run the proper minifier on the file."""
        if ftype == 'js' and hasattr(settings, 'UGLIFY_BIN'):
            o = {'method': 'UglifyJS', 'bin': settings.UGLIFY_BIN}
            call("%s %s -nc -o %s %s" % (o['bin'], self.v, file_out, file_in),
                 shell=True, stdout=PIPE)
        elif ftype == 'css' and hasattr(settings, 'CLEANCSS_BIN'):
            o = {'method': 'clean-css', 'bin': settings.CLEANCSS_BIN}
            call("%s -o %s %s" % (o['bin'], file_out, file_in),
                 shell=True, stdout=PIPE)
        else:
            o = {'method': 'YUI Compressor', 'bin': settings.JAVA_BIN}
            variables = (o['bin'], self.path_to_jar, self.v, file_in, file_out)
            call("%s -jar %s %s %s -o %s" % variables,
                 shell=True, stdout=PIPE)

        print "Minifying %s (using %s)" % (file_in, o['method'])

    def _file_hash(self, url):
        """Open the file and get a hash of it."""
        if url in self.checked_hash:
            return self.checked_hash[url]

        file_hash = ""
        try:
            with open(url) as f:
                file_hash = hashlib.md5(f.read()).hexdigest()[0:7]
        except IOError:
            self.missing_files += 1
            if self.v:
                print " - Could not find file %s" % url

        self.checked_hash[url] = file_hash
        return file_hash

    def _cachebust_regex(self, img, parent):
        """Run over the regex; img is the structural regex object."""
        url = img.group(1).strip('"\'')
        if url.startswith('data:') or url.startswith('http'):
            return "url(%s)" % url

        url = url.split('?')[0]
        full_url = os.path.join(settings.ROOT, os.path.dirname(parent),
                                url)

        return "url(%s?%s)" % (url, self._file_hash(full_url))

