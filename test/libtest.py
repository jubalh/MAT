#!/usr/bin/env python
# -*- coding: utf-8 -*

'''
    Unit test for the library
'''

import unittest
import test
import sys
import tempfile
sys.path.append('..')
import MAT


class TestRemovelib(test.MATTest):
    '''
        test the remove_all() method
    '''
    def test_remove(self):
        '''make sure that the lib remove all compromizing meta'''
        for _, dirty in self.file_list:
            current_file = MAT.mat.create_class_file(dirty, False, add2archive=True, low_pdf_quality=True)
            current_file.remove_all()
            current_file2 = MAT.mat.create_class_file(dirty, False, add2archive=True, low_pdf_quality=True)
            self.assertTrue(current_file2.is_clean())

    def test_remove_empty(self):
        '''Test removal with clean files'''
        for clean, _ in self.file_list:
            current_file = MAT.mat.create_class_file(clean, False, add2archive=True, low_pdf_quality=True)
            current_file.remove_all()
            self.assertTrue(current_file.is_clean())


class TestListlib(test.MATTest):
    '''
        test the get_meta() method
    '''
    def test_list(self):
        '''check if get_meta returns all the expected meta'''
        for _, dirty in self.file_list:
            current_file = MAT.mat.create_class_file(dirty, False, add2archive=True, low_pdf_quality=True)
            #FIXME assertisNotNone() : python 2.7
            self.assertTrue(current_file.get_meta())

    def testlist_list_empty(self):
        '''check that a listing of a clean file return an empty dict'''
        for clean, _ in self.file_list:
            current_file = MAT.mat.create_class_file(clean, False, add2archive=True, low_pdf_quality=True)
            self.assertEqual(current_file.get_meta(), dict())


class TestisCleanlib(test.MATTest):
    '''
        test the is_clean() method
    '''
    def test_dirty(self):
        '''test is_clean on clean files'''
        for _, dirty in self.file_list:
            current_file = MAT.mat.create_class_file(dirty, False, add2archive=True, low_pdf_quality=True)
            self.assertFalse(current_file.is_clean())

    def test_clean(self):
        '''test is_clean on dirty files'''
        for clean, _ in self.file_list:
            current_file = MAT.mat.create_class_file(clean, False, add2archive=True, low_pdf_quality=True)
            self.assertTrue(current_file.is_clean())


class TestFileAttributes(unittest.TestCase):
    '''
        test various stuffs about files (readable, writable, exist, ...)
    '''
    def test_not_writtable(self):
        ''' test MAT's behaviour on non-writable file'''
        self.assertFalse(MAT.mat.create_class_file('not_writtable', False, add2archive=True, low_pdf_quality=True))

    def test_not_exist(self):
        ''' test MAT's behaviour on non-existent file'''
        self.assertFalse(MAT.mat.create_class_file('ilikecookies', False, add2archive=True, low_pdf_quality=True))

    def test_empty(self):
        ''' test MAT's behaviour on empty file'''
        self.assertFalse(MAT.mat.create_class_file('empty_file', False, add2archive=True, low_pdf_quality=True))

class TestSecureRemove(unittest.TestCase):
    ''' Test the secure_remove function
    '''
    def test_remove_existing(self):
        ''' test the secure removal of an existing file
        '''
        _, file_to_remove = tempfile.mkstemp()
        self.assertTrue(MAT.mat.secure_remove(file_to_remove))

    def test_remove_fail(self):
        ''' test the secure removal of an non-removable file
        '''
        self.assertRaises(MAT.exceptions.UnableToRemoveFile, MAT.mat.secure_remove, '/OMAGAD')


def get_tests():
    ''' Return every libtests'''
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRemovelib))
    suite.addTest(unittest.makeSuite(TestListlib))
    suite.addTest(unittest.makeSuite(TestisCleanlib))
    suite.addTest(unittest.makeSuite(TestFileAttributes))
    suite.addTest(unittest.makeSuite(TestSecureRemove))
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=test.VERBOSITY).run(get_tests())
