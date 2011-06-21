'''
    Parent class of all parser
'''

import hachoir_core.error
import hachoir_parser
import hachoir_metadata
import hachoir_editor
import sys

POSTFIX = ".cleaned"

class Generic_parser():
    def __init__(self, realname, filename, parser, editor):
        self.meta = {}
        self.filename = filename
        self.realname = realname
        self.parser = parser
        self.editor = editor
        #self.meta = self.__fill_meta()

    def __fill_meta(self):
        metadata = {}
        try:
            meta = hachoir_metadata.extractMetadata(self.parser)
        except hachoir_core.error.HachoirError, err:
            print("Metadata extraction error: %s" % err)

        if not meta:
            print("Unable to extract metadata from the file %s" % self.filename)
            #sys.exit(1)

        for title in meta:
            #fixme i'm so dirty
            if title.values != []: #if the field is not empty
                value = ""
                for item in title.values:
                    value = item.text
                metadata[title.key] = value
        return metadata

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
        metadata = []
        for field in self.editor:
            if self._should_remove(field):
                metadata.append(field.name)
        return metadata

    def _should_remove(self, key):
        '''
            return True if the field is compromizing
            abstract method
        '''
        raise NotImplementedError()
