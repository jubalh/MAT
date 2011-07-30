'''
    Takes care about pictures formats
'''

import parser


class JpegStripper(parser.GenericParser):
    '''
        Represents a .jpeg file
    '''
    def _should_remove(self, field):
        '''
            return True if the field is compromizing
        '''
        if field.name.startswith('comment'):
            return True
        elif field.name in ("photoshop", "exif", "adobe"):
            return True
        else:
            return False


class PngStripper(parser.GenericParser):
    '''
        Represents a .png file
    '''
    def _should_remove(self, field):
        '''
            return True if the field is compromizing
        '''
        if field.name.startswith("text["):
            return True
        elif field.name is "time":
            return True
        else:
            return False
