''' Take care of archives formats
'''

import logging
import os
import shutil
import tarfile
import tempfile
import zipfile

import mat
import parser


class GenericArchiveStripper(parser.GenericParser):
    ''' Represent a generic archive
    '''
    def __init__(self, filename, parser, mime, backup, is_writable, **kwargs):
        super(GenericArchiveStripper, self).__init__(filename, parser, mime, backup, is_writable, **kwargs)
        self.compression = ''
        self.add2archive = kwargs['add2archive']
        self.tempdir = tempfile.mkdtemp()

    def __del__(self):
        ''' Remove the files inside the temp dir,
            then remove the temp dir
        '''
        for root, dirs, files in os.walk(self.tempdir):
            for item in files:
                path_file = os.path.join(root, item)
                mat.secure_remove(path_file)
        shutil.rmtree(self.tempdir)

    def is_clean(self, list_unsupported):
        raise NotImplementedError

    def list_unsupported(self):
        ''' Get a list of every non-supported files present in the archive
        '''
        return self.is_clean(list_unsupported=True)

    def remove_all(self):
        ''' Virtual method to remove all metadata
        '''
        raise NotImplementedError


class ZipStripper(GenericArchiveStripper):
    ''' Represent a zip file
    '''
    def is_file_clean(self, fileinfo):
        ''' Check if a ZipInfo object is clean of metadatas added
            by zip itself, independently of the corresponding file metadatas
        '''
        if fileinfo.comment != '':
            return False
        elif fileinfo.date_time != (1980, 1, 1, 0, 0, 0):
            return False
        elif fileinfo.create_system != 3:  # 3 is UNIX
            return False
        return True

    def is_clean(self, list_unsupported=False):
        ''' Check if the given file is clean from harmful metadata
        '''
        if list_unsupported:
            ret_list = []
        zipin = zipfile.ZipFile(self.filename, 'r')
        if zipin.comment != '':
            logging.debug('%s has a comment' % self.filename)
            return False
        for item in zipin.infolist():
            # I have not found a way to remove the crap added by zipfile :/
            # if not self.is_file_clean(item):
            #    logging.debug('%s from %s has compromising zipinfo' %
            #        (item.filename, self.filename))
            #    return False
            zipin.extract(item, self.tempdir)
            name = os.path.join(self.tempdir, item.filename)
            if os.path.isfile(name):
                cfile = mat.create_class_file(name, False, add2archive=self.add2archive)
                if cfile:
                    if not cfile.is_clean():
                        return False
                else:
                    logging.info('%s\'s fileformat is not supported, or is harmless' % item.filename)
                    basename, ext = os.path.splitext(name)
                    bname = os.path.basename(item.filename)
                    if ext not in parser.NOMETA:
                        if bname != 'mimetype' and bname != '.rels':
                            if list_unsupported:
                                ret_list.append(bname)
                            else:
                                return False
        zipin.close()
        if list_unsupported:
            return ret_list
        return True

    def get_meta(self):
        ''' Return all the metadata of a ZipFile (don't return metadatas
            of contained files : should it ?)
        '''
        zipin = zipfile.ZipFile(self.filename, 'r')
        metadata = {}
        for field in zipin.infolist():
            zipmeta = {}
            if field.comment != '':
                zipmeta['comment'] = field.comment
            if field.date_time != (1980, 1, 1, 0, 0, 0):
                zipmeta['modified'] = field.date_time
            if field.create_system != 3:  # 3 is UNIX
                zipmeta['system'] = "windows" if field.create_system == 2 else "unknown"
        if zipin.comment != '':
            metadata["%s comment" % self.filename] = zipin.comment
        zipin.close()
        return metadata

    def remove_all(self):
        ''' So far, the zipfile module does not allow to write a ZipInfo
            object into a zipfile (and it's a shame !) : so data added
            by zipfile itself could not be removed. It's a big concern.
            Is shipping a patched version of zipfile.py a good idea ?
        '''
        zipin = zipfile.ZipFile(self.filename, 'r')
        zipout = zipfile.ZipFile(self.output, 'w', allowZip64=True)
        for item in zipin.infolist():
            zipin.extract(item, self.tempdir)
            name = os.path.join(self.tempdir, item.filename)
            if os.path.isfile(name):
                try:
                    cfile = mat.create_class_file(name, False,
                        add2archive=self.add2archive)
                    cfile.remove_all()
                    logging.debug('Processing %s from %s' % (item.filename,
                        self.filename))
                    zipout.write(name, item.filename)
                except:
                    logging.info('%s\'s format is not supported or harmless' %
                        item.filename)
                    _, ext = os.path.splitext(name)
                    if self.add2archive or ext in parser.NOMETA:
                        zipout.write(name, item.filename)
        zipin.close()
        for zipFile in zipout.infolist():
            zipFile.orig_filename = zipFile.filename
            zipFile.date_time = (1980, 1, 1, 0, 0, 0)
            zipFile.create_system = 3  # 3 is UNIX
        zipout.comment = ''
        zipout.close()

        logging.info('%s processed' % self.filename)
        self.do_backup()
        return True


class TarStripper(GenericArchiveStripper):
    ''' Represent a tarfile archive
    '''
    def _remove(self, current_file):
        ''' Remove the meta added by tar itself to the file
        '''
        current_file.mtime = 0
        current_file.uid = 0
        current_file.gid = 0
        current_file.uname = ''
        current_file.gname = ''
        return current_file

    def remove_all(self, exclude_list=[]):
        tarin = tarfile.open(self.filename, 'r' + self.compression, encoding='utf-8')
        tarout = tarfile.open(self.output, 'w' + self.compression, encoding='utf-8')
        for item in tarin.getmembers():
            tarin.extract(item, self.tempdir)
            complete_name = os.path.join(self.tempdir, item.name)
            if item.isfile():
                cfile = mat.create_class_file(complete_name, False, add2archive=self.add2archive)
                if cfile:
                    cfile.remove_all()
                    tarout.add(complete_name, item.name, filter=self._remove)
                else:
                    logging.info('%s\' format is not supported or harmless' % item.name)
                    basename, ext = os.path.splitext(item.name)
                    if self.add2archive or ext in parser.NOMETA:
                        tarout.add(complete_name, item.name, filter=self._remove)
        tarin.close()
        tarout.close()
        self.do_backup()
        return True

    def is_file_clean(self, current_file):
        ''' Check metadatas added by tar
        '''
        if current_file.mtime != 0:
            return False
        elif current_file.uid != 0:
            return False
        elif current_file.gid != 0:
            return False
        elif current_file.uname != '':
            return False
        elif current_file.gname != '':
            return False
        return True

    def is_clean(self, list_unsupported=False):
        ''' Check if the file is clean from harmful metadatas
        '''
        if list_unsupported:
            ret_list = []
        tmp_len = len(self.tempdir) + 1  # trim the tempfile path
        tarin = tarfile.open(self.filename, 'r' + self.compression)
        for item in tarin.getmembers():
            if not self.is_file_clean(item) and not list_unsupported:
                return False
            tarin.extract(item, self.tempdir)
            complete_name = os.path.join(self.tempdir, item.name)
            if item.isfile():
                class_file = mat.create_class_file(complete_name, False, add2archive=self.add2archive)
                if class_file:
                    if not class_file.is_clean():
                        # We don't support nested archives
                        if list_unsupported:
                                if isinstance(class_file, GenericArchiveStripper):
                                    ret_list.append(complete_name[tmp_len:])
                        else:
                            return False
                else:
                    logging.error('%s\'s format is not supported or harmless' % item.name)
                    basename, ext = os.path.splitext(complete_name)
                    if ext not in parser.NOMETA:
                        if list_unsupported:
                            ret_list.append(complete_name[tmp_len:])
                        else:
                            return False
        tarin.close()
        if list_unsupported:
            return ret_list
        return True

    def get_meta(self):
        ''' Return a dict with all the meta of the file
        '''
        tarin = tarfile.open(self.filename, 'r' + self.compression)
        metadata = {}
        for item in tarin.getmembers():
            current_meta = {}
            if item.isfile():
                tarin.extract(item, self.tempdir)
                name = os.path.join(self.tempdir, item.name)
                class_file = mat.create_class_file(name, False, add2archive=self.add2archive)
                if class_file is not None:
                    meta = class_file.get_meta()
                    if meta:
                        current_meta['file'] = str(meta)
                else:
                    logging.error('%s\'s format is not supported or harmless' % item.name)

                if not self.is_file_clean(item):  # if there is meta
                    current_meta['mtime'] = item.mtime
                    current_meta['uid'] = item.uid
                    current_meta['gid'] = item.gid
                    current_meta['uname'] = item.uname
                    current_meta['gname'] = item.gname
                    metadata[item.name] = str(current_meta)
        tarin.close()
        return metadata


class GzipStripper(TarStripper):
    ''' Represent a tar.gz archive
    '''
    def __init__(self, filename, parser, mime, backup, is_writable, **kwargs):
        super(GzipStripper, self).__init__(filename, parser, mime, backup, is_writable, **kwargs)
        self.compression = ':gz'


class Bzip2Stripper(TarStripper):
    ''' Represent a tar.bz2 archive
    '''
    def __init__(self, filename, parser, mime, backup, is_writable, **kwargs):
        super(Bzip2Stripper, self).__init__(filename, parser, mime, backup, is_writable, **kwargs)
        self.compression = ':bz2'
