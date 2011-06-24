import tarfile
import sys
import parser
import mat

class TarStripper(parser.Generic_parser):
    def remove_all(self):
        if not tarfile.is_tarfile(self.filename):
            print('%s is not a valid tar file' % self.filename)
            sys.exit(1)

        tarin = tarfile.open(self.filename, 'r')
        tarout = tarfile.open(self.filename + parser.POSTFIX, 'w')

        for current_file in tarin.getmembers():
            tarin.extract(current_file)
            if current_file.type is '0': #is current_file a regular file ?
                #no backup file
                class_file = mat.create_class_file(current_file.name, False)
                class_file.remove_all()
                tarout.add(current_file.name)

        #meta from the tar itself
        tarout.mtime = None

        tarout.close()
        tarin.close()

    def is_clean(self):
        return False



