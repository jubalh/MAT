import hachoir_core.error
import hachoir_core.cmd_line
import hachoir_parser
import hachoir_metadata

from strippers import *

from hachoir_editor import (createEditor,
    NewFieldSet, EditableInteger, EditableBytes)

import hachoir_editor

import sys

__version__ = "0.1"
__author__ = "jvoisin"


class file():
    def __init__(self, filename):
        self.metadata = {}
        self.clean = False
        self.editor = createEditor(self.parser)
        self.filename = filename
        self.filename, self.realname = hachoir_core.cmd_line.unicodeFilename(
            self.filename), self.filename
        self.parser = hachoir_parser.createParser(self.filename, self.realname)

        if not self.parser:
            print("Unable to parse file : sorry")
            sys.exit(1)

        try:
            self.meta = hachoir_metadata.extractMetadata(self.parser)
        except hachoir_core.error.HachoirError, err:
            print "Metadata extraction error: %s" % unicode(err)
            self.data = None

        if not self.meta:
            print "Unable to extract metadata"
            sys.exit(1)

    def is_clean(self):
        '''
            Return true if the file is clean from any compromizing meta
        '''
        return self.clean

    def remove_all(self):
        '''
            Remove all the files that are compromizing
        '''
        stripEditor(self.editor, self.realname, level, not(values.quiet))
        for key, field in metadata:
            if should_remove(key):
                remove(self, key)

    def remove(self, field):
        '''
            Remove the given file
        '''
        del editor[field]
        return True


    def get_meta(self):
        '''return a dict with all the meta of the file'''
        #FIXME : sooooooooooo dirty !
        for title in self.meta:
            if title.values != []: #if the field is not empty
                value = ""
                for item in title.values:
                    value = item.text
                self.metadata[title.key] = value
        return self.metadata

    def should_remove(self, field):
        '''
            return True if the field is compromizing
            abstract method
        '''
        raise NotImplementedError()

def stripEditor(editor, filename, realname, level, verbose):
    '''
        Assign a stripper to an editor
    '''
    cls = editor.input.__class__
    try:
        stripper_cls = strippers[cls]
    except KeyError:
        print "Don't have stripper for file type: %s" % editor.description
        return False
    stripper = stripper_cls(editor, level, verbose)

    if stripper():
        output = FileOutputStream(filename, realname)
        editor.writeInto(output)

    else:
        print _("Stripper doesn't touch the file")
    return True

file(sys.argv[1]).get_meta()
