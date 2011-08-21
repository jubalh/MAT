'''
    Takes care about pictures formats
'''

import parser


class JpegStripper(parser.GenericParser):
    '''
        represents a jpeg file
    '''
    def _should_remove(self, field):
        '''
            return True if the field is compromizing
        '''
        name = field.name
        if name.startswith('comment'):
            return True
        elif name in ("photoshop", "exif", "adobe"):
            return True
        else:
            return False


class PngStripper(parser.GenericParser):
    '''
        represents a png file
    '''
    def _should_remove(self, field):
        '''
            return True if the field is compromizing
        '''
        name = field.name
        if name.startswith("text[") or name.startswith('utf8_text'):
            return True
        elif name == "time":
            return True
        else:
            return False
