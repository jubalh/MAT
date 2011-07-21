#!/usr/bin/python
'''
    Unit test for the CLI interface
'''

import unittest
import subprocess
import sys

sys.path.append('..')
import cli
from lib import mat
import test

class Test_Remove_cli(test.MATTest):
    def test_remove(self):
        '''make sure that the cli remove all compromizing meta'''
        for clean, dirty in self.file_list:
            subprocess.call(['../cli.py', dirty])
            current_file = mat.create_class_file(dirty, False, True)
            self.assertTrue(current_file.is_clean())

    def test_remove_empty(self):
        '''Test removal with clean files'''
        for clean, dirty in self.file_list:
            subprocess.call(['../cli.py', clean])
            current_file = mat.create_class_file(clean, False, True)
            self.assertTrue(current_file.is_clean())


class Test_List_cli(test.MATTest):
    def test_list_clean(self):
        '''check if get_meta returns meta'''
        for clean, dirty in self.file_list:
            proc = subprocess.Popen(['../cli.py', '-d', clean],
                stdout=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            self.assertEqual(stdout.strip('\n'), "[+] File %s :\nNo harmful meta found" % clean)

    def test_list_dirty(self):
        '''check if get_meta returns all the expected meta'''
        for clean, dirty in self.file_list:
            proc = subprocess.Popen(['../cli.py', '-d', dirty],
                stdout=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            self.assertNotEqual(stdout, "[+] File %s" % dirty)


class Test_isClean_cli(test.MATTest):
    #FIXME : use an external file with string as const ?
    def test_clean(self):
        '''test is_clean on clean files'''
        for clean, dirty in self.file_list:
            proc = subprocess.Popen(['../cli.py', '-c', clean],
                stdout=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            self.assertEqual(stdout.strip('\n'), '[+] %s is clean' % clean)

    def test_dirty(self):
        '''test is_clean on dirty files'''
        for clean, dirty in self.file_list:
            proc = subprocess.Popen(['../cli.py', '-c', dirty],
                stdout=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            self.assertEqual(stdout.strip('\n'), '[+] %s is not clean' % dirty)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test_Remove_cli))
    suite.addTest(unittest.makeSuite(Test_List_cli))
    suite.addTest(unittest.makeSuite(Test_isClean_cli))
    unittest.TextTestRunner(verbosity=2).run(suite)
