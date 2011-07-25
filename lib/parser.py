'''
    Parent class of all parser
'''

import hachoir_core.error
import hachoir_parser
import hachoir_editor

import sys
import os
import subprocess
import mimetypes

import mat

NOMETA = ('*.txt', '*.bmp', '*.py')

class Generic_parser(object):
    def __init__(self, realname, filename, parser, editor, backup, add2archive):
        basename, ext = os.path.splitext(filename)
        self.output = basename + '.cleaned.' + ext
        self.filename = filename #path + filename
        self.realname = realname #path + filename
        self.shortname = os.path.basename(filename) #only filename
        self.mime = mimetypes.guess_type(filename)[0] #mimetype
        self.parser = parser
        self.editor = editor
        self.backup = backup

    def is_clean(self):
        '''
            Check if the file is clean from harmful metadatas
        '''
        for field in self.editor:
            if self._should_remove(field):
                return False
        return True

    def remove_all(self):
        '''
            Remove all the files that are compromizing
        '''
        for field in self.editor:
            if self._should_remove(field):
                self._remove(field.name)
        hachoir_core.field.writeIntoFile(self.editor, self.output)
        self.do_backup()

    def remove_all_ugly(self):
        '''
            If the remove_all() is not efficient enough,
            this method is implemented :
            It is efficient, but destructive.
            In a perfect world, with nice fileformat,
            this method would not exist.
        '''
        self.remove_all()


    def _remove(self, field):
        '''
            Delete the given field
        '''
        del self.editor[field]

    def get_meta(self):
        '''
            return a dict with all the meta of the file
        '''
        metadata = {}
        for field in self.editor:
            if self._should_remove(field):
                try:
                    metadata[field.name] = field.value
                except:
                    metadata[field.name] = 'harmful content'
        return metadata

    def _should_remove(self, key):
        '''
            return True if the field is compromizing
            abstract method
        '''
        raise NotImplementedError()

    def do_backup(self):
        '''
            Do a backup of the file if asked
        '''
        if self.backup is False:
            mat.secure_remove(self.filename)
            os.rename(self.output, self.filename)
