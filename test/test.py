'''
    Class for the testing suite :
	- get the list of all test files
	- create a copy of them on start
	- remove the copy on end
'''

import shutil
import os
import glob
import sys
import tempfile
import unittest

sys.path.append('..')
from lib import mat

VERBOSITY = 3
FILE_LIST = zip(glob.glob('clean*'), glob.glob('dirty*'))

class MATTest(unittest.TestCase):
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
        for clean, dirty in self.file_list:
            mat.secure_remove(clean)
            mat.secure_remove(dirty)
        shutil.rmtree(self.tmpdir)
