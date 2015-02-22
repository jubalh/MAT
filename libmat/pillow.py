''' Care about images with help of PIL.
This class doesn't remove metadata in the "conventional way";
it opens, then saves the image. This should remove unknown metadata.
'''

# FIXME Implement this with a decorator instead

import parser


class PillowStripper(object):
    ''' This class implements a single method, "open_and_save".
        It's a class instead of a function so it can be inherited.
    '''
    def open_and_save(self):
        ''' Open and save the image with PIL.
        This should remove a lot of unknown metadata.
        '''
        try:
            from PIL import Image
        except ImportError:
            logging.error('Unable to import PIL, image support degraded. Be careful.')

        try:
            Image.open(self.filename).save(self.filename)
        except IOError:
            logging.error('Can not save %s.' % self.filename)
