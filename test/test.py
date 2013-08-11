#!/usr/bin/env python
# -*- coding: utf-8 -*

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

VERBOSITY = 15

clean = glob.glob('clean*')
clean.sort()
dirty = glob.glob('dirty*')
dirty.sort()

FILE_LIST = zip(clean, dirty)

try:  # PDF render processing
    import cairo
    import gi
    from gi.repository import Poppler
    import pdfrw
except ImportError:
    FILE_LIST.remove(('clean é.pdf', 'dirty é.pdf'))

try:  # python-mutagen : audio file format
    import mutagen
except ImportError:
    FILE_LIST.remove(('clean é.ogg', 'dirty é.ogg'))
    FILE_LIST.remove(('clean é.mp3', 'dirty é.mp3'))
    FILE_LIST.remove(('clean é.flac', 'dirty é.flac'))

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
            clean_dir = os.path.join(self.tmpdir, clean)
            dirty_dir = os.path.join(self.tmpdir, dirty)
            shutil.copy2(clean, clean_dir)
            shutil.copy2(dirty, dirty_dir)
            self.file_list.append((clean_dir, dirty_dir))

    def tearDown(self):
        '''
            Remove the tmp folder
        '''
        shutil.rmtree(self.tmpdir)


if __name__ == '__main__':
    import clitest
    import libtest

    SUITE = unittest.TestSuite()
    SUITE.addTests(clitest.get_tests())
    SUITE.addTests(libtest.get_tests())

    unittest.TextTestRunner(verbosity=VERBOSITY).run(SUITE)
