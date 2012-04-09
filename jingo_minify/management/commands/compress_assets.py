import hashlib
from optparse import make_option
import shutil
import os
import re
import time
from subprocess import call, PIPE

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
import hashlib
from os.path import normpath, walk, isdir, isfile, dirname, basename,\
    exists as path_exists, join as path_join, getsize


path = lambda *a: os.path.join(settings.STATIC_ROOT, *a)


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
    cmd_errors = False

    def update_hashes(self, update=False):
        build_id_file = os.path.realpath(os.path.join(settings.PROJECT_ROOT,
                                                      'build.py'))
        file_paths = {
            'css': [],
            'js': [],
        }
        for ftype, bundle in settings.MINIFY_BUNDLES.iteritems():
            for files in bundle.itervalues():
                full_paths = map(path, files)
                file_paths[ftype].extend(full_paths)

        with open(build_id_file, 'w') as f:
            settings.MINIFY_BUNDLES
            f.write('BUILD_ID_CSS = "%s"' % self._path_checksum(file_paths['css']))
            f.write("\n")
            f.write('BUILD_ID_JS = "%s"' % self._path_checksum(file_paths['js']))
            f.write("\n")
            f.write('BUILD_ID_IMG = "%s"' % self._path_checksum(path('img')))
            f.write("\n")
            f.write('BUNDLE_HASHES = %s' % self.bundle_hashes)
            f.write("\n")

    def handle(self, **options):
        if options.get('do_update_only', False):
            self.update_hashes(update=True)
            return

        jar_path = (os.path.dirname(__file__), '..', '..', 'bin',
                'yuicompressor-2.4.7.jar')
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
                self._concat_files(files_all, tmp_concatted)

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
        if self.cmd_errors:
            raise CommandError('one or more minify commands exited with a '
                               'non-zero status. See output above for errors.')


    def _path_checksum(self, paths):
        """
        Recursively calculates a checksum representing the contents of all files
        found with a sequence of file and/or directory paths.
        """
        if not hasattr(paths, '__iter__'):
            paths = [paths]

        def _update_checksum(checksum, dirname, filenames):
            for filename in sorted(filenames):
                path = path_join(dirname, filename)
                if isfile(path):
                    checksum.update("blob %u\0" % getsize(path))
                    fh = open(path, 'rb')
                    while 1:
                        buf = fh.read(4096)
                        if not buf : break
                        checksum.update(buf)
                    fh.close()

        checksum = hashlib.sha1()

        for path in sorted([normpath(f) for f in paths]):
            if path_exists(path):
                if isdir(path):
                    walk(path, _update_checksum, checksum)
                elif isfile(path):
                    _update_checksum(checksum, dirname(path), [basename(path)])
            else:
                print "Can't count checksum of path '%s'. Path doesn't exist." % (path)

        return checksum.hexdigest()


    def _call(self, *args, **kw):
        exit = call(*args, **kw)
        if exit != 0:
            self.cmd_errors = True
        return exit

    def _concat_files(self, from_files, to_file):
        destination = open(to_file, 'wb')
        for filename in from_files:
            shutil.copyfileobj(open(filename, 'rb'), destination)
        destination.close()

    def _preprocess_file(self, filename):
        """Preprocess files and return new filenames."""
        if filename.endswith('.less'):
            fp = path(filename.lstrip('/'))
            self._call('%s %s %s.css' % (settings.LESS_BIN, fp, fp),
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
            self._call("%s %s -o %s %s" % (o['bin'], self.v, file_out, file_in),
                 shell=True, stdout=PIPE)
        elif ftype == 'css' and hasattr(settings, 'CLEANCSS_BIN'):
            o = {'method': 'clean-css', 'bin': settings.CLEANCSS_BIN}
            self._call("%s -o %s %s" % (o['bin'], file_out, file_in),
                 shell=True, stdout=PIPE)
        else:
            o = {'method': 'YUI Compressor', 'bin': settings.JAVA_BIN}
            variables = (o['bin'], self.path_to_jar, self.v, file_in, file_out)
            self._call("%s -jar %s %s %s -o %s" % variables,
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
        full_url = os.path.join(settings.PROJECT_ROOT, os.path.dirname(parent),
                                url)

        return "url(%s?%s)" % (url, self._file_hash(full_url))

