import hachoir_core.error
import hachoir_core.cmd_line
import hachoir_parser
import hachoir_metadata
import sys
import mat


class JpegStripper(file):
    def checkField(self, field):
            print(field.description)
            if field.name.startswith("comment"):
                return True
            return field.name in ("photoshop", "exif", "adobe")
        return False


