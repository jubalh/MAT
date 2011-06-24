'''
    Parent class of all parser
'''

import hachoir_core.error
import hachoir_parser
import hachoir_editor
import sys
import os
import shutil

POSTFIX = ".cleaned"

class Generic_parser():
    def __init__(self, realname, filename, parser, editor, backup):
        self.filename = filename
        self.realname = realname
        self.parser = parser
        self.editor = editor
        self.backup = backup

    def secure_remove(self):
        '''
            securely remove the file
        '''
        #FIXME : not secure at all !
        try:
            shutil.rmtree(self.filename)
            #shutil.subprocess('shutil' , '--remove', 'self.filename')
        except:
            print('Unable to remove %s' % self.filename)

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
                self._remove(field)
        hachoir_core.field.writeIntoFile(self.editor, self.filename + POSTFIX)
        if self.backup is False:
            self.secure_remove() #remove the old file
            os.rename(self.filename+ POSTFIX, self.filename)#rename the new

    def remove_all_ugly(self):
        '''
            If the remove_all() is not efficient enough,
            this method is implemented :
            It is efficient, but destructive.
            In a perfect world, with nice fileformat,
            this method does not exist.
        '''
        self.remove_all()


    def _remove(self, field):
        '''
            Remove the given field
        '''
        del self.editor[field.name]

    def search(self, value):
        return self.__search(value, self.editor)

    def __search(self, value, graph):
        '''
            Search a given file
        '''
        for node in graph:
            try:
                iter(node)
                return node.value + self.__search(value, node)
            except:
                if node.name == value:
                    return value
        return False


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
                    metadata[field.name] = "harmful content"
        return metadata

    def _should_remove(self, key):
        '''
            return True if the field is compromizing
            abstract method
        '''
        raise NotImplementedError()
