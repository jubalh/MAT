import parser

class BmpStripper(parser.Generic_parser):
    def _should_remove(self, field):
        return False

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
        if field.name.startswith("text["):
            return True
        elif field.name is "time":
            return True
        else:
            return False
