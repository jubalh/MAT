'''
    Care about images with help of the amazing (perl) library Exiftool.
'''

import subprocess
import parser


class ExiftoolStripper(parser.GenericParser):
    '''
        A generic stripper class using exiftool as backend
    '''

    def __init__(self, filename, parser, mime, backup, add2archive):
        super(ExiftoolStripper, self).__init__(filename, parser, mime,
        backup, add2archive)
        self.allowed = ['ExifTool Version Number', 'File Name', 'Directory',
                'File Size', 'File Modification Date/Time', 'File Permissions',
                'File Type', 'MIME Type', 'Image Width', 'Image Height',
                'Image Size']
        self._set_allowed()

    def _set_allowed(self):
        '''
            Set the allowed/harmless list of metadata
        '''
        raise NotImplementedError

    def remove_all(self):
        '''
            Remove all metadata with help of exiftool
        '''
        if self.backup:
            process = subprocess.Popen(['exiftool', '-all=',
                '-o %s' % self.output, self.filename],
                stdout=open('/dev/null'))
            process.wait()
        else:
            process = subprocess.Popen(['exiftool', '-overwrite_original',
                '-all=', self.filename], stdout=open('/dev/null'))
            process.wait()

    def is_clean(self):
        '''
            Check if the file is clean with help of exiftool
        '''
        out = subprocess.Popen(['exiftool', self.filename],
                stdout=subprocess.PIPE).communicate()[0]
        out = out.split('\n')
        for i in out[:-1]:
            if i.split(':')[0].strip() not in self.allowed:
                return False
        return True

    def get_meta(self):
        '''
            Return every harmful meta with help of exiftool
        '''
        out = subprocess.Popen(['exiftool', self.filename],
                stdout=subprocess.PIPE).communicate()[0]
        out = out.split('\n')
        meta = {}
        for i in out[:-1]:
            key = i.split(':')[0].strip()
            if key not in self.allowed:
                meta[key] = i.split(':')[1].strip()
        return meta


class JpegStripper(ExiftoolStripper):
    '''
        Care about jpeg files with help
        of exiftool
    '''
    def _set_allowed(self):
        self.allowed.extend(['JFIF Version', 'Resolution Unit',
        'X Resolution', 'Y Resolution', 'Encoding Process', 'Bits Per Sample',
        'Color Components', 'Y Cb Cr Sub Sampling'])

class PngStripper(ExiftoolStripper):
    '''
        Care about png files with help
        of exiftool
    '''
    def _set_allowed(self):
        self.allowed.extend(['Bit Depth', 'Color Type', 'Compression',
            'Filter', 'Interlace', 'Pixels Per Unit X', 'Pixels Per Unit Y',
            'Pixel Units'])
