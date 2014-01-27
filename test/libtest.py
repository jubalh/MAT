#!/usr/bin/env python
# -*- coding: utf-8 -*

'''
    Unit test for the library
'''

import os
import sys
import shutil
import tarfile
import tempfile
import test
import unittest

sys.path.append('..')
import MAT


class TestRemovelib(test.MATTest):
    ''' test the remove_all() method
    '''
    def test_remove(self):
        '''make sure that the lib remove all compromizing meta'''
        for _, dirty in self.file_list:
            current_file = MAT.mat.create_class_file(dirty, False, add2archive=True)
            current_file.remove_all()
            current_file = MAT.mat.create_class_file(dirty, False, add2archive=True)
            self.assertTrue(current_file.is_clean())

    def test_remove_empty(self):
        '''Test removal with clean files'''
        for clean, _ in self.file_list:
            current_file = MAT.mat.create_class_file(clean, False, add2archive=True)
            current_file.remove_all()
            current_file = MAT.mat.create_class_file(clean, False, add2archive=True)
            self.assertTrue(current_file.is_clean())


class TestListlib(test.MATTest):
    ''' test the get_meta() method
    '''
    def test_list(self):
        '''check if get_meta returns metadata'''
        for _, dirty in self.file_list:
            current_file = MAT.mat.create_class_file(dirty, False, add2archive=True)
            self.assertIsNotNone(current_file.get_meta())

    def testlist_list_empty(self):
        '''check that a listing of a clean file returns an empty dict'''
        for clean, _ in self.file_list:
            current_file = MAT.mat.create_class_file(clean, False, add2archive=True)
            self.assertEqual(current_file.get_meta(), dict())


class TestisCleanlib(test.MATTest):
    ''' Test the is_clean() method
    '''
    def test_dirty(self):
        '''test is_clean on dirty files'''
        for _, dirty in self.file_list:
            current_file = MAT.mat.create_class_file(dirty, False, add2archive=True)
            self.assertFalse(current_file.is_clean())

    def test_clean(self):
        '''test is_clean on clean files'''
        for clean, _ in self.file_list:
            current_file = MAT.mat.create_class_file(clean, False, add2archive=True)
            self.assertTrue(current_file.is_clean())


class TestFileAttributes(unittest.TestCase):
    '''
        test various stuffs about files (readable, writable, exist, ...)
    '''
    def test_not_writtable(self):
        ''' test MAT's behaviour on non-writable file'''
        self.assertFalse(MAT.mat.create_class_file('not_writtable', False, add2archive=True))

    def test_not_exist(self):
        ''' test MAT's behaviour on non-existent file'''
        self.assertFalse(MAT.mat.create_class_file('ilikecookies', False, add2archive=True))

    def test_empty(self):
        ''' test MAT's behaviour on empty file'''
        self.assertFalse(MAT.mat.create_class_file('empty_file', False, add2archive=True))


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
        self.assertRaises(MAT.exceptions.UnableToWriteFile, MAT.mat.secure_remove, '/NOTREMOVABLE')


class TestArchiveProcessing(test.MATTest):
    ''' Test archives processing
    '''
    def test_remove_bz2(self):
        ''' Test MAT's ability to process .tar.bz2
        '''
        tarpath = os.path.join(self.tmpdir, "test.tar.bz2")
        tar = tarfile.open(tarpath, "w:bz2")
        for clean, dirty in self.file_list:
            tar.add(dirty)
            tar.add(clean)
        tar.close()
        current_file = MAT.mat.create_class_file(tarpath, False, add2archive=False)
        current_file.remove_all()
        current_file = MAT.mat.create_class_file(tarpath, False, add2archive=False)
        self.assertTrue(current_file.is_clean())

    def test_remove_tar(self):
        ''' Test MAT on tar files
        '''
        tarpath = os.path.join(self.tmpdir, "test.tar")
        tar = tarfile.open(tarpath, "w")
        for clean, dirty in self.file_list:
            tar.add(dirty)
            tar.add(clean)
        tar.close()
        current_file = MAT.mat.create_class_file(tarpath, False, add2archive=False)
        current_file.remove_all()
        current_file = MAT.mat.create_class_file(tarpath, False, add2archive=False)
        self.assertTrue(current_file.is_clean())

    def test_remove_gz(self):
        ''' Test MAT on tar.gz files
        '''
        tarpath = os.path.join(self.tmpdir, "test.tar.gz")
        tar = tarfile.open(tarpath, "w")
        for clean, dirty in self.file_list:
            tar.add(dirty)
            tar.add(clean)
        tar.close()
        current_file = MAT.mat.create_class_file(tarpath, False, add2archive=False)
        current_file.remove_all()
        current_file = MAT.mat.create_class_file(tarpath, False, add2archive=False)
        self.assertTrue(current_file.is_clean())

    def test_get_unsupported(self):
        ''' Test the get_unsupported feature, used by the GUI
        '''
        tarpath = os.path.join(self.tmpdir, "test.tar.bz2")
        tar = tarfile.open(tarpath, "w")
        for f in ('../mat.desktop', '../README.security', '../setup.py'):
            tar.add(f, f[3:])  # trim '../'
        tar.close()
        current_file = MAT.mat.create_class_file(tarpath, False, add2archive=False)
        unsupported_files = set(current_file.is_clean(list_unsupported=True))
        self.assertEqual(unsupported_files, set(('mat.desktop', 'README.security', 'setup.py')))

    def test_archive_unwritable_content(self):
        path = os.path.join(self.tmpdir, './unwritable_content.zip')
        shutil.copy2('./unwritable_content.zip', self.tmpdir)
        current_file = MAT.mat.create_class_file(path, False, add2archive=False)
        current_file.remove_all()
        current_file = MAT.mat.create_class_file(path, False, add2archive=False)
        self.assertTrue(current_file.is_clean())

def get_tests():
    ''' Returns every libtests'''
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRemovelib))
    suite.addTest(unittest.makeSuite(TestListlib))
    suite.addTest(unittest.makeSuite(TestisCleanlib))
    suite.addTest(unittest.makeSuite(TestFileAttributes))
    suite.addTest(unittest.makeSuite(TestSecureRemove))
    suite.addTest(unittest.makeSuite(TestArchiveProcessing))
    return suite
