import parser
import pdfrw
import os
import mat
import subprocess
import tempfile
import glob

class PdfStripper(parser.Generic_parser):
    '''
        Represent a pdf file, with the help of pdfrw
    '''
    def __init__(self, filename, backup):
        self.filename = filename
        self.backup = backup
        self.trailer = pdfrw.PdfReader(self.filename)
        self.writer = pdfrw.PdfWriter()

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
        output_file = self.filename + parser.POSTFIX + '.pdf'
        _, self.tmpdir = tempfile.mkstemp()
        subprocess.call('gm convert %s %s' % (self.filename, self.tmpdir +
            'temp.jpg'), shell=True)
        for current_file in glob.glob(self.tmpdir + 'temp*'):
            class_file = mat.create_class_file(current_file, False)
            class_file.remove_all()
        subprocess.call('gm convert %s %s' % (self.tmpdir +
            'temp.jpg*', output_file), shell=True)
        for current_file in glob.glob(self.tmpdir + 'temp*'):
            mat.secure_remove(current_file)
        if self.backup is False:
            mat.secure_remove(self.filename) #remove the old file
            os.rename(output_file, self.filename)#rename the new
            name = self.filename
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

