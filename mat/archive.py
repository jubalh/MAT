'''
    Take care of archives formats
'''

import zipfile
import shutil
import os
import logging
import tempfile

import parser
import mat
from tarfile import tarfile


class GenericArchiveStripper(parser.GenericParser):
    '''
        Represent a generic archive
    '''
    def __init__(self, filename, parser, mime, backup, add2archive):
        super(GenericArchiveStripper, self).__init__(filename, parser, mime,
        backup, add2archive)
        self.compression = ''
        self.add2archive = add2archive
        self.tempdir = tempfile.mkdtemp()

    def __del__(self):
        '''
            Remove the files inside the temp dir,
            then remove the temp dir
        '''
        for root, dirs, files in os.walk(self.tempdir):
            for item in files:
                path_file = os.path.join(root, item)
                mat.secure_remove(path_file)
        shutil.rmtree(self.tempdir)

    def remove_all(self):
        '''
            Call _remove_all() with in argument : "normal"
        '''
        return self._remove_all('normal')

    def remove_all_ugly(self):
        '''
            call remove_all() with in argument : "ugly"
        '''
        return self._remove_all('ugly')

    def _remove_all(self, method):
        '''
            Remove all meta, normal way if method is "normal",
            else, use the ugly way (with possible data loss)
        '''
        raise NotImplementedError


class ZipStripper(GenericArchiveStripper):
    '''
        Represent a zip file
    '''
    def is_file_clean(self, fileinfo):
        '''
            Check if a ZipInfo object is clean of metadatas added
            by zip itself, independently of the corresponding file metadatas
        '''
        if fileinfo.comment is not '':
            return False
        elif fileinfo.date_time is not 0:
            return False
        elif fileinfo.create_system is not 0:
            return False
        elif fileinfo.create_version is not 0:
            return False
        else:
            return True

    def is_clean(self):
        '''
            Check if the given file is clean from harmful metadata
        '''
        zipin = zipfile.ZipFile(self.filename, 'r')
        if zipin.comment != '':
            logging.debug('%s has a comment' % self.filename)
            return False
        for item in zipin.infolist():
            #I have not found a way to remove the crap added by zipfile :/
            #if not self.is_file_clean(item):
            #    logging.debug('%s from %s has compromizing zipinfo' %
            #        (item.filename, self.filename))
            #    return False
            zipin.extract(item, self.tempdir)
            name = os.path.join(self.tempdir, item.filename)
            if os.path.isfile(name):
                try:
                    cfile = mat.create_class_file(name, False,
                        self.add2archive)
                    if not cfile.is_clean():
                        return False
                except:
                    #best solution I have found
                    logging.info('%s\'s fileformat is not supported, or is a \
harmless format' % item.filename)
                    _, ext = os.path.splitext(name)
                    bname = os.path.basename(item.filename)
                    if ext not in parser.NOMETA:
                        if bname != 'mimetype' and bname != '.rels':
                            return False
        zipin.close()
        return True

    def get_meta(self):
        '''
            Return all the metadata of a ZipFile (don't return metadatas
            of contained files : should it ?)
        '''
        zipin = zipfile.ZipFile(self.filename, 'r')
        metadata = {}
        for field in zipin.infolist():
            zipmeta = {}
            zipmeta['comment'] = field.comment
            zipmeta['modified'] = field.date_time
            zipmeta['system'] = field.create_system
            zipmeta['zip_version'] = field.create_version
            metadata[field.filename] = zipmeta
        metadata["%s comment" % self.filename] = zipin.comment
        zipin.close()
        return metadata

    def _remove_all(self, method):
        '''
            So far, the zipfile module does not allow to write a ZipInfo
            object into a zipfile (and it's a shame !) : so data added
            by zipfile itself could not be removed. It's a big concern.
            Is shiping a patched version of zipfile.py a good idea ?
        '''
        zipin = zipfile.ZipFile(self.filename, 'r')
        zipout = zipfile.ZipFile(self.output, 'w', allowZip64=True)
        for item in zipin.infolist():
            zipin.extract(item, self.tempdir)
            name = os.path.join(self.tempdir, item.filename)
            if os.path.isfile(name):
                try:
                    cfile = mat.create_class_file(name, False,
                        self.add2archive)
                    if method is 'normal':
                        cfile.remove_all()
                    else:
                        cfile.remove_all_ugly()
                    logging.debug('Processing %s from %s' % (item.filename,
                        self.filename))
                    zipout.write(name, item.filename)
                except:
                    logging.info('%s\'s format is not supported or harmless' %
                        item.filename)
                    _, ext = os.path.splitext(name)
                    if self.add2archive or ext in parser.NOMETA:
                        zipout.write(name, item.filename)
        zipout.comment = ''
        zipin.close()
        zipout.close()
        logging.info('%s treated' % self.filename)
        self.do_backup()
        return True


class TarStripper(GenericArchiveStripper):
    '''
        Represent a tarfile archive
    '''
    def _remove(self, current_file):
        '''
            remove the meta added by tar itself to the file
        '''
        current_file.mtime = 0
        current_file.uid = 0
        current_file.gid = 0
        current_file.uname = ''
        current_file.gname = ''
        return current_file

    def _remove_all(self, method):
        tarin = tarfile.open(self.filename, 'r' + self.compression)
        tarout = tarfile.open(self.output, 'w' + self.compression)
        for item in tarin.getmembers():
            tarin.extract(item, self.tempdir)
            name = os.path.join(self.tempdir, item.name)
            if item.type is '0':  # is item a regular file ?
                #no backup file
                try:
                    cfile = mat.create_class_file(name, False,
                    self.add2archive)
                    if method is 'normal':
                        cfile.remove_all()
                    else:
                        cfile.remove_all_ugly()
                    tarout.add(name, item.name, filter=self._remove)
                except:
                    logging.info('%s\' format is not supported or harmless' %
                        item.name)
                    _, ext = os.path.splitext(name)
                    if self.add2archive or ext in parser.NOMETA:
                        tarout.add(name, item.name, filter=self._remove)
        tarin.close()
        tarout.close()
        self.do_backup()
        return True

    def is_file_clean(self, current_file):
        '''
            Check metadatas added by tar
        '''
        if current_file.mtime is not 0:
            return False
        elif current_file.uid is not 0:
            return False
        elif current_file.gid is not 0:
            return False
        elif current_file.uname is not '':
            return False
        elif current_file.gname is not '':
            return False
        else:
            return True

    def is_clean(self):
        '''
            Check if the file is clean from harmful metadatas
        '''
        tarin = tarfile.open(self.filename, 'r' + self.compression)
        for item in tarin.getmembers():
            if not self.is_file_clean(item):
                tarin.close()
                return False
            tarin.extract(item, self.tempdir)
            name = os.path.join(self.tempdir, item.name)
            if item.type is '0':  # is item a regular file ?
                try:
                    class_file = mat.create_class_file(name,
                        False, self.add2archive)  # no backup file
                    if not class_file.is_clean():
                        tarin.close()
                        return False
                except:
                    logging.error('%s\'s foramt is not supported or harmless' %
                        item.filename)
                    _, ext = os.path.splitext(name)
                    if ext not in parser.NOMETA:
                        tarin.close()
                        return False
        tarin.close()
        return True

    def get_meta(self):
        '''
            Return a dict with all the meta of the file
        '''
        tarin = tarfile.open(self.filename, 'r' + self.compression)
        metadata = {}
        for current_file in tarin.getmembers():
            if current_file.type is '0':
                if not self.is_file_clean(current_file):  # if there is meta
                    current_meta = {}
                    current_meta['mtime'] = current_file.mtime
                    current_meta['uid'] = current_file.uid
                    current_meta['gid'] = current_file.gid
                    current_meta['uname'] = current_file.uname
                    current_meta['gname'] = current_file.gname
                    metadata[current_file.name] = current_meta
        tarin.close()
        return metadata


class GzipStripper(TarStripper):
    '''
        Represent a tar.gz archive
    '''
    def __init__(self, filename, parser, mime, backup, add2archive):
        super(GzipStripper, self).__init__(filename, parser, mime, backup,
            add2archive)
        self.compression = ':gz'


class Bzip2Stripper(TarStripper):
    '''
        Represents a tar.bz2 archive
    '''
    def __init__(self, filename, parser, mime, backup, add2archive):
        super(Bzip2Stripper, self).__init__(filename, parser, mime, backup,
            add2archive)
        self.compression = ':bz2'
