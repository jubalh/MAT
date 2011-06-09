import cli
import unittest
import test

import shlex
import subprocess

class Test_Remove_cli(test.MATTest):
    def test_remove(self):
        '''make sure that the cli remove all compromizing meta'''
        for clean, dirty in self.file_list:
            subprocess.call("cli.py %s" dirty)
            self.assertTrue(mat.file(dirty).is_clean())

    def test_remove_empty(self):
        '''Test removal with clean files'''
        for clean, dirty in self.file_list:
            subprocess.call("cli.py %s" clean)
            self.assertTrue(mat.file(dirty).is_clean())


class Test_List_cli(test.MATTest):
    def test_list(self):
        '''check if get_meta returns all the expected meta'''
        for clean, dirty in self.file_list:
            meta_list = dict("fixme":"please",) #FIXME
            self.assertDictEqual(mat.file(dirty).get_meta(), meta_list)

    def testlist_list_empty(self):
        '''check that a listing of a clean file return an empty dict'''
        for clean, dirty in self.file_list:
            self.assertEqual(mat.file(clean).get_meta(), None)


class Test_isClean_cli(test.MATTest):
    def test_clean(self):
        '''test is_clean on clean files'''
        for clean, dirty in self.file_list:
            print "e"
            self.assertTrue(mat.file(clean).is_clean())

    def test_clean(self):
        '''test is_clean on dirty files'''
        for clean, dirty in self.file_list:
            self.assertFalse(mat.file(dirty).is_clean())


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test_Remove))
    suite.addTest(unittest.makeSuite(Test_List))
    suite.addTest(unittest.makeSuite(Test_isClean))
    unittest.TextTestRunner(verbosity=2).run(suite)

