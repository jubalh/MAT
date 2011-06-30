import tarfile
import sys
import parser
import mat
import shutil
import os

class TarStripper(parser.Generic_parser):
    def __init__(self, realname, filename, parser, editor, backup):
        super(TarStripper, self).__init__(realname,
            filename, parser, editor, backup)
        self.compression = ''
        self.tarin = tarfile.open(self.filename, 'r' + self.compression)
        self.folder_list = []

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

    def remove_all(self):
        self.tarin = tarfile.open(self.filename, 'r' + self.compression)
        self.tarout = tarfile.open(self.filename + parser.POSTFIX,
            'w' + self.compression)
        for current_file in self.tarin.getmembers():
            self.tarin.extract(current_file)
            if current_file.type is '0': #is current_file a regular file ?
                #no backup file
                class_file = mat.create_class_file(current_file.name, False)
                class_file.remove_all()
                self.tarout.add(current_file.name, filter=self._remove)
                mat.secure_remove(current_file.name)
            else:
                self.folder_list.insert(0, current_file.name)
        self.tarin.close()
        self.tarout.close()

        for folder in self.folder_list: #delete remainings folders
            shutil.rmtree(folder)

        if self.backup is False:
            mat.secure_remove(self.filename)
            os.rename(self.filename + parser.POSTFIX, self.filename)

    def is_clean(self):
        self.tarin = tarfile.open(self.filename, 'r' + self.compression)
        for current_file in self.tarin.getmembers():
            self.tarin.extract(current_file)
            if current_file.type is '0': #is current_file a regular file ?
                #no backup file
                class_file = mat.create_class_file(current_file.name, False)
                if not class_file.is_clean():
                    self.folder_list = []
                    return False
                mat.secure_remove(current_file.name)
            else:
                self.folder_list.insert(0, current_file.name)
        self.tarin.close()

        for folder in self.folder_list: #delete remainings folders
            shutil.rmtree(folder)
        self.folder_list = []
        return False

    def get_meta(self):
        self.tarin = tarfile.open(self.filename, 'r' + self.compression)
        metadata = {}
        for current_file in self.tarin.getmembers():
            if current_file.type is '0':
                current_meta = {}
                current_meta['mtime'] = current_file.mtime
                current_meta['uid'] = current_file.uid
                current_meta['gid'] = current_file.gid
                current_meta['uname'] = current_file.uname
                current_meta['gname'] = current_file.gname
                metadata[current_file.name] = current_meta
        return metadata

class GzipStripper(TarStripper):
    def __init__(self, realname, filename, parser, editor, backup):
        super(GzipStripper, self).__init__(realname,
            filename, parser, editor, backup)
        self.compression = ':gz'

class Bzip2Stripper(TarStripper):
    def __init__(self, realname, filename, parser, editor, backup):
        super(Bzip2Stripper, self).__init__(realname,
            filename, parser, editor, backup)
        self.compression = ':bz2'
