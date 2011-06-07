import mat
import unittest
import shutil
import glob
import tempfile

FILE_LIST = zip(glob.glob('clean*'), glob.glob('dirty*'))

class MATTest(unittest.TestCase):
    def setUp(self):
	'''create working copy of the clean and the dirty file in the TMP dir'''
	self.file_list = []
	self.tmpdir = tempfile.mkdtemp()

	for clean, dirty in FILE_LIST:
	    shutil.copy2(clean, self.tmpdir + clean)
	    shutil.copy2(dirty, self.tmpdir + dirty)
	    self.file_list.append((self.tmpdir + clean, self.tmpdir + dirty))

    def tearDown(self):
	'''Remove the tmp folder'''
	shutil.rmtree(self.tmpdir)

class Test_Remove(MATTest):
    def test_remove(self):
        '''make sure that the lib remove all compromizing meta'''
        for clean, dirty in self.file_list:
            mat.file(dirty).remove_all()
            self.assertTrue(mat.file(dirty).is_clean())

    def test_remove_empty(self):
        '''Test removal with clean files'''
        for clean, dirty in self.file_list:
            mat.file(clean).remove_all()
            self.assertTrue(mat.file(clean).is_clean())


class Test_List(MATTest):
    def test_list(self):
        '''check if get_meta returns all the expected meta'''
        for clean, dirty in self.file_list:
            meta_list = dict() #FIXME
            self.assertDictEqual(mat.file(dirty).get_meta(), meta_list)

    def testlist_list_empty(self):
        '''check that a listing of a clean file return an empty dict'''
        for clean, dirty in self.file_list:
            self.assertEqual(mat.file(clean).get_meta(), None)


class Test_isClean(MATTest):
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

