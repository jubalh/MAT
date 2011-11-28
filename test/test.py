'''
    Class for the testing suite :
    - get the list of all test files
    - create a copy of them on start
    - remove the copy on end
'''

import shutil
import os
import glob
import tempfile
import unittest
import subprocess

VERBOSITY = 3

clean = glob.glob('clean*')
clean.sort()
dirty  = glob.glob('dirty*')
dirty.sort()

FILE_LIST = zip(clean, dirty)

try:  # pdf render processing
    import poppler
    import cairo
except:
    FILE_LIST.remove(('clean.pdf', 'dirty.pdf'))

try:  # python-mutagen : audio file format
    import mutagen
except:
    FILE_LIST.remove(('clean.ogg', 'dirty.ogg'))

try:  # file format managed by exiftool
    subprocess.Popen('exiftool', stdout=open('/dev/null'))
except:
    pass  # None for now


class MATTest(unittest.TestCase):
    '''
        Parent class of all test-functions
    '''
    def setUp(self):
        '''
            Create working copy of the clean and the dirty file in the TMP dir
        '''
        self.file_list = []
        self.tmpdir = tempfile.mkdtemp()

        for clean, dirty in FILE_LIST:
            shutil.copy2(clean, self.tmpdir + os.sep + clean)
            shutil.copy2(dirty, self.tmpdir + os.sep + dirty)
            self.file_list.append((self.tmpdir + os.sep + clean,
                self.tmpdir + os.sep + dirty))

    def tearDown(self):
        '''
            Remove the tmp folder
        '''
        shutil.rmtree(self.tmpdir)
