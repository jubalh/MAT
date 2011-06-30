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

FILE_LIST = zip(glob.glob('clean*'), glob.glob('dirty*'))

class MATTest(unittest.TestCase):
    def setUp(self):
	'''create working copy of the clean and the dirty file in the TMP dir'''
        self.file_list = []
        _, self.tmpdir = tempfile.mkstemp()

        for clean, dirty in FILE_LIST:
            shutil.copy2(clean, self.tmpdir + clean)
            shutil.copy2(dirty, self.tmpdir + dirty)
            self.file_list.append((self.tmpdir + clean, self.tmpdir + dirty))

    def tearDown(self):
	'''Remove the tmp folder'''
        for root, dirs, files in os.walk(self.tmpdir, topdown=False):
            for name in files:
                mat.secure_remove(os.path.join(toor, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
