#!/usr/bin/python
'''
    Unit test for the CLI interface
'''

import unittest
import subprocess
import sys

sys.path.append('..')
from mat import mat
import test

class TestRemovecli(test.MATTest):
    '''
        test if cli correctly remove metadatas
    '''
    def test_remove(self):
        '''make sure that the cli remove all compromizing meta'''
        for _, dirty in self.file_list:
            subprocess.call(['../mat-cli', dirty])
            current_file = mat.create_class_file(dirty, False, True)
            self.assertTrue(current_file.is_clean())

    def test_remove_empty(self):
        '''Test removal with clean files'''
        for clean, _ in self.file_list:
            subprocess.call(['../mat-cli', clean])
            current_file = mat.create_class_file(clean, False, True)
            self.assertTrue(current_file.is_clean())


class TestListcli(test.MATTest):
    '''
        test if cli correctly display metadatas
    '''
    def test_list_clean(self):
        '''check if get_meta returns meta'''
        for clean, _ in self.file_list:
            proc = subprocess.Popen(['../mat-cli', '-d', clean],
                stdout=subprocess.PIPE)
            stdout, _ = proc.communicate()
            self.assertEqual(stdout.strip('\n'), "[+] File %s :\nNo harmful \
meta found" % clean)

    def test_list_dirty(self):
        '''check if get_meta returns all the expected meta'''
        for _, dirty in self.file_list:
            proc = subprocess.Popen(['../mat-cli', '-d', dirty],
                stdout=subprocess.PIPE)
            stdout, _ = proc.communicate()
            self.assertNotEqual(stdout, "[+] File %s" % dirty)


class TestisCleancli(test.MATTest):
    '''
        check if cli correctly check if a file is clean or not
    '''
    def test_clean(self):
        '''test is_clean on clean files'''
        for clean, _ in self.file_list:
            proc = subprocess.Popen(['../mat-cli', '-c', clean],
                stdout=subprocess.PIPE)
            stdout, _ = proc.communicate()
            self.assertEqual(stdout.strip('\n'), '[+] %s is clean' % clean)

    def test_dirty(self):
        '''test is_clean on dirty files'''
        for _, dirty in self.file_list:
            proc = subprocess.Popen(['../mat-cli', '-c', dirty],
                stdout=subprocess.PIPE)
            stdout, _ = proc.communicate()
            self.assertEqual(stdout.strip('\n'), '[+] %s is not clean' % dirty)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRemovecli))
    suite.addTest(unittest.makeSuite(TestListcli))
    suite.addTest(unittest.makeSuite(TestisCleancli))
    unittest.TextTestRunner(verbosity=test.VERBOSITY).run(suite)
