'''
    Care about images with help of the amazing (perl) library Exiftool.
'''

import subprocess
import images
import parser

class JpegStripper(parser.GenericParser):
    '''
        Care about jpeg files with help
        of exiftool
    '''
    def remove_all(self):
        '''
            Remove all metadata with help of exiftool
        '''
        subprocess.Popen('exiftool -filename=%s -all= %s' %
                (self.output, self.filename))

