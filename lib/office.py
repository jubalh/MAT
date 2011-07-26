import os
import mimetypes
import subprocess
import tempfile
import glob
import logging
import zipfile
import re
from xml.etree import ElementTree


import pdfrw
import mat
import parser
import archive


class OpenDocumentStripper(archive.GenericArchiveStripper):
    '''
        An open document file is a zip, with xml file into.
        The one that interest us is meta.xml
    '''

    def get_meta(self):
        zipin = zipfile.ZipFile(self.filename, 'r')
        metadata = {}
        try:
            content = zipin.read('meta.xml')
            zipin.close()
            tree = ElementTree.fromstring(content)
            for node in tree.iter():
                key = re.sub('{.*}', '', node.tag)
                metadata[key] = node.text
        except KeyError:  # no meta.xml file found
            logging.debug('%s has no opendocument metadata' % self.filename)
        return metadata

    def _remove_all(self, method):
        '''
            FIXME ?
            There is a patch implementing the Zipfile.remove()
            method here : http://bugs.python.org/issue6818
        '''
        zipin = zipfile.ZipFile(self.filename, 'r')
        zipout = zipfile.ZipFile(self.output, 'w',
            allowZip64=True)
        for item in zipin.namelist():
            name = os.path.join(self.tempdir, item)
            if item.endswith('.xml') or item == 'mimetype':
                #keep .xml files, and the "manifest" file
                if item != 'meta.xml':  # contains the metadata
                    zipin.extract(item, self.tempdir)
                    zipout.write(name, item)
                    mat.secure_remove(name)
            elif item.endswith('manifest.xml'):
                zipin.extract(item, self.tempdir)
                #remove line meta.xml
                zipout.write(name, item)
                mat.secure_remove(name)
            else:
                zipin.extract(item, self.tempdir)
                if os.path.isfile(name):
                    try:
                        cfile = mat.create_class_file(name, False,
                            self.add2archive)
                        if method == 'normal':
                            cfile.remove_all()
                        else:
                            cfile.remove_all_ugly()
                        logging.debug('Processing %s from %s' % (item,
                            self.filename))
                        zipout.write(name, item)
                    except:
                        logging.info('%s\' fileformat is not supported' % item)
                        if self.add2archive:
                            zipout.write(name, item)
                    mat.secure_remove(name)
        zipout.comment = ''
        logging.info('%s treated' % self.filename)
        zipin.close()
        zipout.close()
        self.do_backup()

    def is_clean(self):
        zipin = zipfile.ZipFile(self.filename, 'r')
        try:
            zipin.getinfo('meta.xml')
            return False
        except KeyError:  # no meta.xml in the file
                zipin.close()
                czf = archive.ZipStripper(self.realname, self.filename,
                    self.parser, self.editor, self.backup, self.add2archive)
                if czf.is_clean():
                    return True
                else:
                    return False
        return True


class PdfStripper(parser.Generic_parser):
    '''
        Represent a pdf file, with the help of pdfrw
    '''
    def __init__(self, filename, realname, backup):
        name, ext = os.path.splitext(filename)
        self.output = name + '.cleaned' + ext
        self.filename = filename
        self.backup = backup
        self.realname = realname
        self.shortname = os.path.basename(filename)
        self.mime = mimetypes.guess_type(filename)[0]
        self.trailer = pdfrw.PdfReader(self.filename)
        self.writer = pdfrw.PdfWriter()
        self.convert = 'gm convert -antialias -enhance %s %s'

    def remove_all(self):
        '''
            Remove all the meta fields that are compromizing
        '''
        self.trailer.Info.Title = ''
        self.trailer.Info.Author = ''
        self.trailer.Info.Producer = ''
        self.trailer.Info.Creator = ''
        self.trailer.Info.CreationDate = ''
        self.trailer.Info.ModDate = ''

        self.writer.trailer = self.trailer
        self.writer.write(self.output)
        self.do_backup()

    def remove_all_ugly(self):
        '''
            Transform each pages into a jpg, clean them,
            then re-assemble them into a new pdf
        '''
        _, self.tmpdir = tempfile.mkstemp()
        subprocess.call(self.convert % (self.filename, self.tmpdir +
            'temp.jpg'), shell=True)  # Convert pages to jpg

        for current_file in glob.glob(self.tmpdir + 'temp*'):
        #Clean every jpg image
            class_file = mat.create_class_file(current_file, False)
            class_file.remove_all()

        subprocess.call(self.convert % (self.tmpdir +
            'temp.jpg*', self.output), shell=True)  # Assemble jpg into pdf

        for current_file in glob.glob(self.tmpdir + 'temp*'):
        #remove jpg files
            mat.secure_remove(current_file)

        if self.backup is False:
            mat.secure_remove(self.filename)  # remove the old file
            os.rename(self.output, self.filename)  # rename the new
            name = self.realname
        else:
            name = self.output
        class_file = mat.create_class_file(name, False)
        class_file.remove_all()

    def is_clean(self):
        '''
            Check if the file is clean from harmful metadatas
        '''
        for field in self.trailer.Info:
            if field != '':
                return False
        return True

    def get_meta(self):
        '''
            return a dict with all the meta of the file
        '''
        metadata = {}
        for key, value in self.trailer.Info.iteritems():
                metadata[key[1:]] = value[1:-1]
        return metadata
