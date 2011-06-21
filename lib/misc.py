import parser
import pdfrw

class PdfStripper(parser.Generic_parser):
    '''
        Represent a pdf file, with the help of pdfrw
    '''
    def __init__(self, filename):
        self.filename = filename
        self.trailer = pdfrw.PdfReader(self.filename)
        self.writer = pdfrw.PdfWriter()

    def remove_all(self):
        '''
            Remove all the files that are compromizing
        '''
        self.trailer.Info.Title = ''
        self.trailer.Info.Author = ''
        self.trailer.Info.Producer = ''
        self.trailer.Info.Creator = ''
        self.trailer.Info.CreationDate = ''
        self.trailer.Info.ModDate = ''

        self.writer.trailer = self.trailer
        self.writer.write(self.filename + parser.POSTFIX)

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

