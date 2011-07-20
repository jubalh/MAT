#!/usr/bin/env python

'''
    Metadata anonymisation toolkit library
'''

import os
import subprocess
import logging

import hachoir_core.cmd_line
import hachoir_parser
import hachoir_editor

import images
import audio
import misc
import archive

__version__ = "0.1"
__author__ = "jvoisin"

LOGGING_LEVEL = logging.DEBUG

logging.basicConfig(level = LOGGING_LEVEL)

strippers = {
    hachoir_parser.image.JpegFile: images.JpegStripper,
    hachoir_parser.image.PngFile: images.PngStripper,
    hachoir_parser.audio.MpegAudioFile: audio.MpegAudioStripper,
    hachoir_parser.misc.PDFDocument: misc.PdfStripper,
    hachoir_parser.archive.TarFile: archive.TarStripper,
    hachoir_parser.archive.gzip_parser.GzipParser: archive.GzipStripper,
    hachoir_parser.archive.bzip2_parser.Bzip2Parser: archive.Bzip2Stripper,
}

def secure_remove(filename):
    '''
        securely remove the file
    '''
    try:
        subprocess.call('shred --remove %s' % filename, shell=True)
    except:
        logging.error('Unable to remove %s' % filename)


def is_secure(filename):
    '''
        Prevent shell injection
    '''

    if not(os.path.isfile(filename)): #check if the file exist
        logging.error("Error: %s is not a valid file" % filename)
        return

def create_class_file(name, backup):
    '''
        return a $FILETYPEStripper() class,
        corresponding to the filetype of the given file
    '''
    is_secure(name)

    filename = ""
    realname = name
    filename = hachoir_core.cmd_line.unicodeFilename(name)
    parser = hachoir_parser.createParser(filename)
    if not parser:
        logging.error("Unable to parse %s" % filename)
        return

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
        logging.error("Don't have stripper for file type %s" % editor.description)
        return
    if editor.input.__class__ == hachoir_parser.misc.PDFDocument:
        return stripper_class(filename, realname, backup)
    return stripper_class(realname, filename, parser, editor, backup)
