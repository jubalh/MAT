'''
    Care about images with help of the amazing (perl) library Exiftool.
'''

import subprocess
import images
import parser

class Jpeg_Stripper(images.JpegStripper):
    '''
        Care about jpeg files with help
        of exiftool
    '''
    def remove_all(self):
        '''
            Remove all metadata with help of exiftool
        '''
        subprocess.Popen(['exiftool', '-filename=', self.output,
                '-all= ', self.filename])

