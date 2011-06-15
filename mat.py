#!/usr/bin/python

'''
    Metadata anonymisation toolkit library
'''

import hachoir_core.error
import hachoir_core.cmd_line
import hachoir_parser
import hachoir_metadata
import hachoir_editor

import sys
import os
import hachoir_parser.image

__version__ = "0.1"
__author__ = "jvoisin"


class file():
    def __init__(self, realname, filename, parser, editor):
        self.meta = {}
        self.clean = False
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
            Return true if the file is clean from any compromizing meta
        '''
        return self.clean

    def remove_all(self):
        '''
            Remove all the files that are compromizing
        '''
        for key, field in self.meta.iteritems():
            if self._should_remove(key):
                print "BLEH" #DEBUG
                #_remove(self, key)
        #self.clean = True

    def _remove(self, field):
        '''
            Remove the given file
        '''
        del self.editor[field]


    def get_meta(self):
        '''
            return a dict with all the meta of the file
        '''
        return self.meta

    def get_harmful(self):
        '''
            return a dict with all the harmfull meta of the file
        '''
        harmful = {}
        for key, value in self.meta.iteritems():
            if self._should_remove(key):
                harmful[key] = value
        return harmful



    def _should_remove(self, key):
        '''
            return True if the field is compromizing
            abstract method
        '''
        raise NotImplementedError()

class JpegStripper(file):
    def _should_remove(self, key):
        if key in ('comment', 'author'):
            return True
        else:
            return False

class PngStripper(file):
    def _should_remove(self, key):
        if key in ('comment', 'author'):
            return True
        else:
            return False
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
    parser = hachoir_parser.createParser(filename, realname)
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
