''' Takes care about pictures formats

References:
    - JFIF: http://www.ecma-international.org/publications/techreports/E-TR-098.htm
    - PNG: http://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/PNG.html
    - PNG: http://www.w3.org/TR/PNG-Chunks.html
'''

import parser
import pillow


class ImageStripper(parser.GenericParser, pillow.PillowStripper):
    ''' Common stripper for images.
    Its purpose is to open then save
    images with PIL, the goal being to remove
    unknown metadata.
    '''
    def remove_all(self):
        self.open_and_save()
        super(ImageStripper, self).remove_all()


class JpegStripper(ImageStripper):
    ''' Represents a jpeg file.
        Custom Huffman and Quantization tables
        are stripped: they may leak
        some info, and the quality loss is minor.
    '''
    def _should_remove(self, field):
        ''' Return True if the field is compromising
        '''
        field_list = frozenset([
            'start_image',  # start of the image
            'app0',         # JFIF data
            'start_frame',  # specify width, height, number of components
            'start_scan',   # specify which slice of data the top-to-bottom scan contains
            'data',         # actual data
            'end_image'])   # end of the image
        if field.name in field_list:
            return False
        elif field.name.startswith('quantization['):  # custom Quant. tables
            return False
        elif field.name.startswith('huffman['):  # custom Huffman tables
            return False
        return True


class PngStripper(ImageStripper):
    ''' Represents a png file
    '''
    def _should_remove(self, field):
        ''' Return True if the field is compromising
        '''
        field_list = frozenset([
            'id',
            'header',    # PNG header
            'physical',  # the intended pixel size or aspect ratio
            'end'])      # end of the image
        if field.name in field_list:
            return False
        if field.name.startswith('data['):  # data
            return False
        return True
