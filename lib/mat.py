#!/usr/bin/python

'''
    Metadata anonymisation toolkit library
'''

import sys
import os

import hachoir_core.cmd_line
import hachoir_parser
import hachoir_editor

import images

__version__ = "0.1"
__author__ = "jvoisin"

strippers = {
    hachoir_parser.image.JpegFile: images.JpegStripper,
    hachoir_parser.image.PngFile: images.PngStripper,
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
