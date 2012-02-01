'''
    Care about misc formats
'''

import parser

from bencode import bencode


class TorrentStripper(parser.GenericParser):
    '''
        Represent a torrent file with the help
        of the bencode lib from Petru Paler
    '''
    def __init__(self, filename, parser, mime, backup, add2archive):
        super(TorrentStripper, self).__init__(filename, parser, mime,
            backup, add2archive)
        self.fields = ['comment', 'creation date', 'created by']

    def is_clean(self):
        '''
            Check if the file is clean from harmful metadatas
        '''
        with open(self.filename, 'r') as f:
            decoded = bencode.bdecode(f.read())
        for key in self.fields:
            try:
                if decoded[key] != '':
                    return False
            except:
                pass
        return True

    def get_meta(self):
        '''
            Return a dict with all the meta of the file
        '''
        metadata = {}
        with open(self.filename, 'r') as f:
            decoded = bencode.bdecode(f.read())
        for key in self.fields:
            try:
                if decoded[key] != '':
                    metadata[key] = decoded[key]
            except:
                pass
        return metadata

    def remove_all(self):
        '''
            Remove all the files that are compromizing
        '''
        with open(self.filename, 'r') as f:
            decoded = bencode.bdecode(f.read())
        for key in self.fields:
            try:
                decoded[key] = ''
            except:
                pass
        with open(self.output, 'w') as f:  # encode the decoded torrent
            f.write(bencode.bencode(decoded))  # and write it in self.output
        self.do_backup()
        return True
