import parser

class TarStripper(parser.Generic_parser):
    def remove_all(self):
        for file in self.editor.array("file"):
            print file.name
