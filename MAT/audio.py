'''
    Care about audio fileformat
'''

try:
    from mutagen.flac import FLAC
    from mutagen.oggvorbis import OggVorbis
except ImportError:
    pass

import parser
import mutagenstripper


class MpegAudioStripper(parser.GenericParser):
    '''
        Represent mpeg audio file (mp3, ...)
    '''
    def _should_remove(self, field):
        return field.name in ("id3v1", "id3v2")


class OggStripper(mutagenstripper.MutagenStripper):
    '''
        Represent an ogg vorbis file
    '''
    def _create_mfile(self):
        self.mfile = OggVorbis(self.filename)


class FlacStripper(mutagenstripper.MutagenStripper):
    '''
        Represent a Flac audio file
    '''
    def _create_mfile(self):
        self.mfile = FLAC(self.filename)

    def remove_all(self):
        '''
            Remove the "metadata" block from the file
        '''
        super(FlacStripper, self).remove_all()
        self.mfile.clear_pictures()
        self.mfile.save()
        return True

    def is_clean(self):
        '''
            Check if the "metadata" block is present in the file
        '''
        return super(FlacStripper, self).is_clean() and not self.mfile.pictures

    def get_meta(self):
        '''
            Return the content of the metadata block if present
        '''
        metadata = super(FlacStripper, self).get_meta()
        if self.mfile.pictures:
            metadata['picture:'] = 'yes'
        return metadata
