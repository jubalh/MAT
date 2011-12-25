#!/usr/bin/python

'''
    Unit test for the library
'''

import unittest
import test
import sys
sys.path.append('..')
from mat import mat


class TestRemovelib(test.MATTest):
    '''
        test the remove_all() method
    '''
    def test_remove(self):
        '''make sure that the lib remove all compromizing meta'''
        for _, dirty in self.file_list:
            current_file = mat.create_class_file(dirty, False, True)
            current_file.remove_all()
            current_file2 = mat.create_class_file(dirty, False, True)
            self.assertTrue(current_file2.is_clean())

    def test_remove_empty(self):
        '''Test removal with clean files'''
        for clean, _ in self.file_list:
            current_file = mat.create_class_file(clean, False, True)
            current_file.remove_all()
            self.assertTrue(current_file.is_clean())


class TestListlib(test.MATTest):
    '''
        test the get_meta() method
    '''
    def test_list(self):
        '''check if get_meta returns all the expected meta'''
        for _, dirty in self.file_list:
            current_file = mat.create_class_file(dirty, False, True)
            #FIXME assertisNotNone() : python 2.7
            self.assertTrue(current_file.get_meta())

    def testlist_list_empty(self):
        '''check that a listing of a clean file return an empty dict'''
        for clean, _ in self.file_list:
            current_file = mat.create_class_file(clean, False, True)
            self.assertEqual(current_file.get_meta(), dict())


class TestisCleanlib(test.MATTest):
    '''
        test the is_clean() method
    '''
    def test_dirty(self):
        '''test is_clean on clean files'''
        for _, dirty in self.file_list:
            current_file = mat.create_class_file(dirty, False, True)
            self.assertFalse(current_file.is_clean())

    def test_clean(self):
        '''test is_clean on dirty files'''
        for clean, _ in self.file_list:
            current_file = mat.create_class_file(clean, False, True)
            self.assertTrue(current_file.is_clean())


class TestFileAttributes(unittest.TestCase):
    '''
        test various stuffs about files (readable, writable, exist, ...)
    '''
    def test_not_readable(self):
        self.assertFalse(mat.create_class_file('not_readable', False, True))

    def test_not_writtable(self):
        self.assertFalse(mat.create_class_file('not_writtable', False, True))

    def test_not_exist(self):
        self.assertFalse(mat.create_class_file('ilikecookies', False, True))


def main():
    Suite = unittest.TestSuite()
    Suite.addTest(unittest.makeSuite(TestRemovelib))
    Suite.addTest(unittest.makeSuite(TestListlib))
    Suite.addTest(unittest.makeSuite(TestisCleanlib))
    Suite.addTest(unittest.makeSuite(TestFileAttributes))
    test_result = unittest.TextTestRunner(verbosity=test.VERBOSITY).run(Suite)
    return len(test_result.failures)


if __name__ == '__main__':
    sys.exit(main())
