'''
    Care about audio fileformat
'''
from mutagen.flac import FLAC

import parser
import shutil

class MpegAudioStripper(parser.GenericParser):
    '''
        Represent mpeg audio file (mp3, ...)
    '''
    def _should_remove(self, field):
        if field.name in ("id3v1", "id3v2"):
            return True
        else:
            return False

class FlacStripper(parser.GenericParser):
    '''
        Represent a Flac audio file
    '''
    def remove_all(self):
        '''
            Remove the "metadata" block from the file
        '''
        if self.backup is True:
            shutil.copy2(self.filename, self.output)
            self.filename = self.output

        mfile = FLAC(self.filename)
        mfile.delete()
        mfile.save()

    def is_clean(self):
        '''
            Check if the "metadata" block is present in the file
        '''
        mfile = FLAC(self.filename)
        if mfile.tags is None:
            return True
        else:
            return False

    def get_meta(self):
        '''
            Return the content of the metadata block if present
        '''
        metadata = {}
        mfile = FLAC(self.filename)
        if mfile.tags is None:
            return metadata
        for key, value in mfile.tags:
            metadata[key] = value
        return metadata
