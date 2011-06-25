import tarfile
import sys
import parser
import mat
import shutil

class TarStripper(parser.Generic_parser):
    def remove_all(self):
        if not tarfile.is_tarfile(self.filename):
            print('%s is not a valid tar file' % self.filename)
            sys.exit(1)

        tarin = tarfile.open(self.filename, 'r')
        tarout = tarfile.open(self.filename + parser.POSTFIX, 'w')
        folder_list = []

        for current_file in tarin.getmembers():
            tarin.extract(current_file)
            if current_file.type is '0': #is current_file a regular file ?
                #no backup file
                class_file = mat.create_class_file(current_file.name, False)
                class_file.remove_all()
                tarout.add(current_file.name)
                class_file.secure_remove()
            else:
                folder_list.insert(0, current_file.name)

        for folder in folder_list: #delete remainings folders
            shutil.rmtree(folder)

        #meta from the tar itself
        tarout.mtime = None

        tarout.close()
        tarin.close()

    def is_clean(self):
        return False
