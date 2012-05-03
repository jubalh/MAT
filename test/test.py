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
import sys

VERBOSITY = 3

clean = glob.glob('clean*')
clean.sort()
dirty = glob.glob('dirty*')
dirty.sort()

FILE_LIST = zip(clean, dirty)

try:  # PDF render processing
    import poppler
    import cairo
except:
    FILE_LIST.remove(('clean é.pdf', 'dirty é.pdf'))

try:  # python-mutagen : audio file format
    import mutagen
except:
    pass  # since wr don't have any ogg for now
    #FILE_LIST.remove(('clean.ogg', 'dirty.ogg'))

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


def main():
    import clitest
    import libtest

    failed_tests = 0

    print('Running cli related tests:\n')
    failed_tests += clitest.main()
    print('\nRunning library related tests:\n')
    failed_tests += libtest.main()
    print('\nTotal failed tests: ' + str(failed_tests))
    return failed_tests

if __name__ == '__main__':
    sys.exit(main())
