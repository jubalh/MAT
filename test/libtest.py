#!/usr/bin/python

'''
    Unit test for the library
'''

import unittest
import test
import sys
sys.path.append('..')
from lib import mat

class Test_Remove_lib(test.MATTest):
    def test_remove(self):
        '''make sure that the lib remove all compromizing meta'''
        for clean, dirty in self.file_list:
            current_file = mat.create_class_file(dirty, False, True)
            current_file.remove_all()
            self.assertTrue(current_file.is_clean())

    def test_remove_empty(self):
        '''Test removal with clean files'''
        for clean, dirty in self.file_list:
            current_file = mat.create_class_file(clean, False, True)
            current_file.remove_all()
            self.assertTrue(current_file.is_clean())


class Test_List_lib(test.MATTest):
    def test_list(self):
        '''check if get_meta returns all the expected meta'''
        for clean, dirty in self.file_list:
            current_file = mat.create_class_file(dirty, False, True)
            #FIXME assertisNotNone() : python 2.7
            self.assertTrue(current_file.get_meta())

    def testlist_list_empty(self):
        '''check that a listing of a clean file return an empty dict'''
        for clean, dirty in self.file_list:
            current_file = mat.create_class_file(clean, False, True)
            self.assertEqual(current_file.get_meta(), dict())


class Test_isClean_lib(test.MATTest):
    def test_dirty(self):
        '''test is_clean on clean files'''
        for clean, dirty in self.file_list:
            current_file = mat.create_class_file(dirty, False, True)
            self.assertFalse(current_file.is_clean())

    def test_clean(self):
        '''test is_clean on dirty files'''
        for clean, dirty in self.file_list:
            current_file = mat.create_class_file(clean, False, True)
            self.assertTrue(current_file.is_clean())


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test_Remove_lib))
    suite.addTest(unittest.makeSuite(Test_List_lib))
    suite.addTest(unittest.makeSuite(Test_isClean_lib))
    unittest.TextTestRunner(verbosity=2).run(suite)

