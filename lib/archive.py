import tarfile
import sys
import parser
import mat
import shutil

class TarStripper(parser.Generic_parser):
    def __init__(self, realname, filename, parser, editor, backup):
        super(TarStripper, self).__init__(realname,
            filename, parser, editor, backup)
        self.compression = ''
        self.tarin = tarfile.open(self.filename, 'r' + self.compression)
        self.folder_list = []

    def remove_all(self):
        self.tarout = tarfile.open(self.filename + parser.POSTFIX,
            'w' + self.compression)
        for current_file in self.tarin.getmembers():
            self.tarin.extract(current_file)
            if current_file.type is '0': #is current_file a regular file ?
                #no backup file
                class_file = mat.create_class_file(current_file.name, False)
                class_file.remove_all()
                self.tarout.add(current_file.name)
                mat.secure_remove(current_file.name)
            else:
                self.folder_list.insert(0, current_file.name)

        for folder in self.folder_list: #delete remainings folders
            shutil.rmtree(folder)

        #meta from the tar itself
        self.tarout.mtime = None

        self.tarout.close()
        self.tarin.close()

    def is_clean(self):
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
