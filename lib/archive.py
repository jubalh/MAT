import tarfile
import zipfile

import shutil
import os
import logging
import tempfile

import parser
import mat

class GenericArchiveStripper(parser.Generic_parser):
    '''
        Represent a generic archive
    '''
    def __init__(self, realname, filename, parser, editor, backup, add2archive):
        super(GenericArchiveStripper, self).__init__(realname,
            filename, parser, editor, backup, add2archive)
        self.compression = ''
        self.add2archive = add2archive
        self.tempdir = tempfile.mkdtemp()

    def __del__(self):
        '''
            Remove the temp dir
        '''
        shutil.rmtree(self.tempdir)

    def remove_all(self):
        self._remove_all('normal')

    def remove_all_ugly(self):
        self._remove_all('ugly')

class ZipStripper(GenericArchiveStripper):
    '''
        Represent a zip file
    '''
    def is_file_clean(self, file):
        if file.comment is not '':
            return False
        elif file.date_time is not 0:
            return False
        elif file.create_system is not 0:
            return False
        elif file.create_version is not 0:
            return False
        else:
            return True

    def is_clean(self):
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
                    logging.error('%s is not supported' % item.filename)
                    _, ext = os.path.splitext(name)
                    if ext not in parser.NOMETA:
                        return False
                mat.secure_remove(name)
        zipin.close()
        return True

    def get_meta(self):
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
        zipout = zipfile.ZipFile(self.output, 'w',
            allowZip64=True)
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
                    logging.info('%s\' fileformat is not supported' %
                        item.filename)
                    if self.add2archive:
                        zipout.write(name, item.filename)
                mat.secure_remove(name)
        zipout.comment = ''
        zipin.close()
        zipout.close()
        logging.info('%s treated' % self.filename)
        self.do_backup()


class TarStripper(GenericArchiveStripper):
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
            if item.type is '0': #is item a regular file ?
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
                    logging.info('%s\' format is not supported' %
                        item.name)
                    if self.add2archive:
                        tarout.add(name, item.name,filter=self._remove)
                mat.secure_remove(name)
        tarin.close()
        tarout.close()
        self.do_backup()

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
        tarin = tarfile.open(self.filename, 'r' + self.compression)
        for item in tarin.getmembers():
            if not self.is_file_clean(item):
                return False
            tarin.extract(item, self.tempdir)
            name = os.path.join(self.tempdir, item.name)
            if item.type is '0': #is item a regular file ?
                #no backup file
                try:
                    class_file = mat.create_class_file(name,
                        False, self.add2archive)
                    if not class_file.is_clean():
                        return False
                except:
                    #best solution I have found
                    logging.error('%s is not supported' % item.filename)
                    _, ext = os.path.splitext(name)
                    if ext not in parser.NOMETA:
                        return False
                mat.secure_remove(name)
        tarin.close()
        return True

    def get_meta(self):
        tarin = tarfile.open(self.filename, 'r' + self.compression)
        metadata = {}
        for current_file in tarin.getmembers():
            if current_file.type is '0':
                if not self.is_file_clean(current_file):#if there is meta
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
    def __init__(self, realname, filename, parser, editor, backup, add2archive):
        super(GzipStripper, self).__init__(realname,
            filename, parser, editor, backup, add2archive)
        self.compression = ':gz'


class Bzip2Stripper(TarStripper):
    def __init__(self, realname, filename, parser, editor, backup, add2archive):
        super(Bzip2Stripper, self).__init__(realname,
            filename, parser, editor, backup, add2archive)
        self.compression = ':bz2'
