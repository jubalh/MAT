#!/usr/bin/python

'''
    Metadata anonymisation toolkit library
'''

import hachoir_core.error
import hachoir_core.field
import hachoir_core.cmd_line
import hachoir_parser
import hachoir_metadata
import hachoir_editor

import sys
import os
import hachoir_parser.image

__version__ = "0.1"
__author__ = "jvoisin"

POSTFIX = ".cleaned"

class file():
    def __init__(self, realname, filename, parser, editor):
        self.meta = {}
        self.filename = filename
        self.realname = realname
        self.parser = parser
        self.editor = editor
        self.meta = self.__fill_meta()

    def __fill_meta(self):
        metadata = {}
        try:
            meta = hachoir_metadata.extractMetadata(self.parser)
        except hachoir_core.error.HachoirError, err:
            print("Metadata extraction error: %s" % err)

        if not meta:
            print("Unable to extract metadata from the file %s" % self.filename)
            sys.exit(1)

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


    def get_meta(self):
        '''
            return a dict with all the meta of the file
        '''
        #am I useless ?
        return self.meta

    def _should_remove(self, key):
        '''
            return True if the field is compromizing
            abstract method
        '''
        raise NotImplementedError()

class JpegStripper(file):
    def _should_remove(self, field):
        if field.name.startswith('comment'):
            return True
        elif field.name in ("photoshop", "exif", "adobe"):
            return True
        else:
            return False

class PngStripper(file):
    def _should_remove(self, field):
        if field.name in ('comment'):
            return True
        else:
            return False

strippers = {
    hachoir_parser.image.JpegFile: JpegStripper,
    hachoir_parser.image.PngFile: PngStripper,
}

def create_class_file(name):
    '''
        return a $FILETYPEStripper() class,
        corresponding to the filetype of the given file
    '''
    if not(os.path.isfile(name)): #check if the file exist
        print("Error: %s is not a valid file" % name)
        sys.exit(1)

    filename = ""
    realname = name
    filename = hachoir_core.cmd_line.unicodeFilename(name)
    parser = hachoir_parser.createParser(filename)
    if not parser:
        print("Unable to parse the file %s : sorry" % filename)
        sys.exit(1)

    editor = hachoir_editor.createEditor(parser)
    try:
        '''this part is a little tricky :
        stripper_class will receice the name of the class $FILETYPEStripper,
        (which herits from the "file" class), based on the editor
        of given file (name)
        '''
        stripper_class = strippers[editor.input.__class__]
    except KeyError:
        #Place for another lib than hachoir
        print("Don't have stripper for file type: %s" % editor.description)
        sys.exit(1)
    return stripper_class(realname, filename, parser, editor)
