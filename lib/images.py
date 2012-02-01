'''
    Takes care about pictures formats
'''

import parser


class JpegStripper(parser.GenericParser):
    '''
        represents a jpeg file
        remaining :
        http://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/CanonRaw.html
    '''
    def _should_remove(self, field):
        '''
            return True if the field is compromizing
        '''
        name = field.name
        if name.startswith('comment'):
            return True
        elif name in ('photoshop', 'exif', 'adobe', 'app12'):
            return True
        elif name in ('icc'):  # should we remove the icc profile ?
            return True
        else:
            return False


class PngStripper(parser.GenericParser):
    '''
        represents a png file
        see : http://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/PNG.html
    '''
    def _should_remove(self, field):
        '''
            return True if the field is compromizing
        '''
        name = field.name
        if name.startswith('text['):  # textual meta
            return True
        elif name.startswith('utf8_text['):  # uncompressed adobe crap
            return True
        elif name.startswith('compt_text['):  # compressed adobe crap
            return True
        elif name == "time":  # timestamp
            return True
        else:
            return False
