'''
    Parent class of all parser
'''

import hachoir_core
import hachoir_editor

import os

import mat

NOMETA = ('.bmp', '.rdf', '.txt', '.xml', '.rels')
#bmp : image
#rdf : text
#txt : plain text
#xml : formated text
#rels : openxml foramted text


FIELD = object()

class GenericParser(object):
    '''
        Parent class of all parsers
    '''
    def __init__(self, filename, parser, mime, backup, add2archive):
        self.filename = ''
        self.parser = parser
        self.mime = mime
        self.backup = backup
        self.editor = hachoir_editor.createEditor(parser)
        self.realname = filename
        try:
            self.filename = hachoir_core.cmd_line.unicodeFilename(filename)
        except TypeError:  # get rid of "decoding Unicode is not supported"
            self.filename = filename
        basename, ext = os.path.splitext(filename)
        self.output = basename + '.cleaned' + ext
        self.basename = os.path.basename(filename)  # only filename

    def is_clean(self):
        '''
            Check if the file is clean from harmful metadatas
        '''
        for field in self.editor:
            if self._should_remove(field):
                return self._is_clean(self.editor)
        return True

    def _is_clean(self, fieldset):
        for field in fieldset:
            remove = self._should_remove(field)
            if remove is True:
                return False
            if remove is FIELD:
                if not self._is_clean(field):
                    return False
        return True

    def remove_all(self):
        '''
            Remove all the files that are compromizing
        '''
        self._remove_all(self.editor)
        hachoir_core.field.writeIntoFile(self.editor, self.output)
        self.do_backup()

    def _remove_all(self, fieldset):
        for field in fieldset:
            remove = self._should_remove(field)
            if remove is True:
                self._remove(fieldset, field.name)
            if remove is FIELD:
                self._remove_all(field)

    def remove_all_ugly(self):
        '''
            If the remove_all() is not efficient enough,
            this method is implemented :
            It is efficient, but destructive.
            In a perfect world, with nice fileformat,
            this method would not exist.
        '''
        self.remove_all()

    def _remove(self, fieldset, field):
        '''
            Delete the given field
        '''
        del fieldset[field]

    def get_meta(self):
        '''
            Return a dict with all the meta of the file
        '''
        metadata = {}
        self._get_meta(self.editor, metadata)
        return metadata

    def _get_meta(self, fieldset, metadata):
        for field in fieldset:
            remove = self._should_remove(field)
            if remove is True:
                try:
                    metadata[field.name] = field.value
                except:
                    metadata[field.name] = 'harmful content'
            if remove is FIELD:
                self._get_meta(field)

    def _should_remove(self, key):
        '''
            return True if the field is compromizing
            abstract method
        '''
        raise NotImplementedError

    def do_backup(self):
        '''
            Do a backup of the file if asked,
            and change his creation/access date
        '''
        if self.backup is False:
            mat.secure_remove(self.filename)
            os.rename(self.output, self.filename)
