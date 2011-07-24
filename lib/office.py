import os
import mimetypes
import subprocess
import tempfile
import glob
import logging
import zipfile
import shutil

import hachoir_core

import pdfrw
import mat
import parser
import archive

class OpenDocumentStripper(archive.GenericArchiveStripper):
    '''
        An open document file is a zip, with xml file into.
        The one that interest us is meta.xml
    '''

    def _remove_all(self, method):
        '''
            FIXME ?
            There is a patch implementing the Zipfile.remove()
            method here : http://bugs.python.org/issue6818
        '''
        zipin = zipfile.ZipFile(self.filename, 'r')
        zipout = zipfile.ZipFile(self.filename + parser.POSTFIX, 'w',
            allowZip64=True)
        for item in zipin.namelist():
            name = os.path.join(self.tempdir, item)
            if item.endswith('.xml') or item == 'mimetype':
                #keep .xml files, and the "manifest" file
                if item != 'meta.xml':#contains the metadata
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
                        logging.info('%s\' fileformat is not supported' %
                            item)
                        if self.add2archive:
                            zipout.write(item, name)
                    mat.secure_remove(name)
        zipout.comment = ''
        logging.info('%s treated' % self.filename)
        zipin.close()
        zipout.close()

        if self.backup is False:
            mat.secure_remove(self.filename) #remove the old file
            os.rename(self.filename + parser.POSTFIX, self.filename)

    def is_clean(self):
        zipin = zipfile.ZipFile(self.filename, 'r')
        try:
            zipin.getinfo('meta.xml')
        except KeyError:#no meta.xml in the file
                zipin.close()
                czf = archive.ZipStripper(self.realname, self.filename,
                    self.parser, self.editor, self.backup, self.add2archive)
                if czf.is_clean():
                    return True
                else:
                    return False
        return False


class TorrentStripper(parser.Generic_parser):
    '''
        A torrent file looks like:
        -root
            -start
            -announce
            -announce-list
            -comment
            -created_by
            -creation_date
            -encoding
            -info
            -end
    '''
    def remove_all(self):
        for field in self.editor['root']:
            if self._should_remove(field):
                #FIXME : hachoir does not support torrent metadata editing :<
                del self.editor['/root/' + field.name]
        hachoir_core.field.writeIntoFile(self.editor,
            self.filename + parser.POSTFIX)
        if self.backup is False:
            mat.secure_remove(self.filename) #remove the old file
            os.rename(self.filename + parser.POSTFIX, self.filename)

    def is_clean(self):
        for field in self.editor['root']:
            if self._should_remove(field):
                return False
        return True

    def get_meta(self):
        metadata = {}
        for field in self.editor['root']:
            if self._should_remove(field):
                try:#FIXME
                    metadata[field.name] = field.value
                except:
                    metadata[field.name] = 'harmful content'
        return metadata

    def _should_remove(self, field):
        if field.name in ('comment', 'created_by', 'creation_date', 'info'):
            return True
        else:
            return False


class PdfStripper(parser.Generic_parser):
    '''
        Represent a pdf file, with the help of pdfrw
    '''
    def __init__(self, filename, realname, backup):
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
        self.writer.write(self.filename + parser.POSTFIX)
        if self.backup is False:
            mat.secure_remove(self.filename) #remove the old file
            os.rename(self.filename + parser.POSTFIX, self.filename)

    def remove_all_ugly(self):
        '''
            Transform each pages into a jpg, clean them,
            then re-assemble them into a new pdf
        '''
        output_file = self.realname + parser.POSTFIX + '.pdf'
        _, self.tmpdir = tempfile.mkstemp()
        subprocess.call(self.convert % (self.filename, self.tmpdir +
            'temp.jpg'), shell=True)#Convert pages to jpg

        for current_file in glob.glob(self.tmpdir + 'temp*'):
        #Clean every jpg image
            class_file = mat.create_class_file(current_file, False)
            class_file.remove_all()

        subprocess.call(self.convert % (self.tmpdir +
            'temp.jpg*', output_file), shell=True)#Assemble jpg into pdf

        for current_file in glob.glob(self.tmpdir + 'temp*'):
        #remove jpg files
            mat.secure_remove(current_file)

        if self.backup is False:
            mat.secure_remove(self.filename) #remove the old file
            os.rename(output_file, self.filename)#rename the new
            name = self.realname
        else:
            name = output_file
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
