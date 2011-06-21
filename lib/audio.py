import parser

class MpegAudioStripper(parser.Generic_parser):
    def _should_remove(self, field):
        if field.name in ("id3v1", "id3v2"):
            return True
        else:
            return False
