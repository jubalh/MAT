'''
    Care about images with help of the amazing (perl) library Exiftool.
'''

import subprocess
import images


class JpegStripper(images.JpegStripper):
    '''
        Care about jpeg files with help
        of exiftool
    '''
    ALLOWED = ['ExifTool Version Number', 'File Name', 'Directory',
        'File Size', 'File Modification Date/Time', 'File Permissions',
        'File Type', 'MIME Type', 'JFIF Version', 'Resolution Unit',
        'X Resolution', 'Y Resolution', 'Image Width', 'Image Height',
        'Encoding Process', 'Bits Per Sample', 'Color Components',
        'Y Cb Cr Sub Sampling', 'Image Size']

    def remove_all(self):
        '''
            Remove all metadata with help of exiftool
        '''
        if self.backup:
            process = subprocess.Popen(['exiftool', '-all=',
                '-o %s' % self.output, self.filename])
            #, stdout=open('/dev/null'))
            process.wait()
        else:
            process = subprocess.Popen(['exiftool', '-overwrite_original',
                    '-all=', self.filename])  # , stdout=open('/dev/null'))
            process.wait()

    def is_clean(self):
        '''
            Check if the file is clean
        '''
        out = subprocess.Popen(['exiftool', self.filename],
                stdout=subprocess.PIPE).communicate()[0]
        out = out.split('\n')
        for i in out[:-1]:
            if i.split(':')[0].strip() not in self.ALLOWED:
                return False
        return True

    def get_meta(self):  # FIXME: UGLY
        out = subprocess.Popen(['exiftool', self.filename],
                stdout=subprocess.PIPE).communicate()[0]
        out = out.split('\n')
        meta = {}
        for i in out[:-1]:
            key = i.split(':')[0].strip()
            if key not in self.ALLOWED:
                meta[key] = i.split(':')[1].strip()
        return meta
