import parser

class JpegStripper(parser.Generic_parser):
    def _should_remove(self, field):
        if field.name.startswith('comment'):
            return True
        elif field.name in ("photoshop", "exif", "adobe"):
            return True
        else:
            return False

class PngStripper(parser.Generic_parser):
    def _should_remove(self, field):
        if field.name in ('comment'):
            return True
        else:
            return False
