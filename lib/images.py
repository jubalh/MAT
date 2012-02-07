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
        field_list = frozeset(['start_image', 'app0', 'start_frame',
                'start_scan', 'data', 'end_image'])
        if field.name in field_list:
            return False
        elif field.name.startswith('quantization['):
            return False
        elif field.name.startswith('huffman['):
            return False
        return True


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
