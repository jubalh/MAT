import parser


class MpegAudioStripper(parser.GenericParser):
    '''
        mpeg audio file (mp3, ...)
    '''
    def _should_remove(self, field):
        if field.name in ("id3v1", "id3v2"):
            return True
        else:
            return False

class FlacStripper(parser.GenericParser):
    pass
