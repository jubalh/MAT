#!/usr/bin/env python

'''
    Metadata anonymisation toolkit library
'''

import os
import subprocess
import logging
import xml.sax

import hachoir_core.cmd_line
import hachoir_parser

import images
import audio
import office
import archive

__version__ = '0.1'
__author__ = 'jvoisin'

LOGGING_LEVEL = logging.DEBUG

logging.basicConfig(level=LOGGING_LEVEL)

STRIPPERS = {
    'application/x-tar': archive.TarStripper,
    'application/x-gzip': archive.GzipStripper,
    'application/x-bzip2': archive.Bzip2Stripper,
    'application/zip': archive.ZipStripper,
    'audio/mpeg': audio.MpegAudioStripper,
    'image/jpeg': images.JpegStripper,
    'image/png': images.PngStripper,
    'application/vnd.oasis.opendocument': office.OpenDocumentStripper,
}

try:
    import poppler
    import cairo
    STRIPPERS['application/x-pdf'] = office.PdfStripper
    STRIPPERS['application/pdf'] = office.PdfStripper
except ImportError:
    print('Unable to import python-poppler and/or python-cairo: no pdf support')

try:
    import mutagen
    STRIPPERS['audio/x-flac'] = audio.FlacStripper
    STRIPPERS['audio/vorbis'] = audio.OggStripper
except ImportError:
    print('unable to import python-mutagen : limited audio format support')


class XMLParser(xml.sax.handler.ContentHandler):
    '''
        Parse the supported format xml, and return a corresponding
        list of dict
    '''
    def __init__(self):
        self.dict = {}
        self.list = []
        self.content, self.key = '', ''
        self.between= False

    def startElement(self, name, attrs):
        '''
            Called when entering into xml balise
        '''
        self.between = True
        self.key = name
        self.content = ''

    def endElement(self, name):
        '''
            Called when exiting a xml balise
        '''
        if name == 'format':  # exiting a fileformat section
            self.list.append(self.dict.copy())
            self.dict.clear()
        else:
            content = self.content.replace('\n', ' ')
            self.dict[self.key] = content
            self.between = False

    def characters(self, characters):
        '''
            Concatenate the content between opening and closing balises
        '''
        if self.between is True:
            self.content += characters


def secure_remove(filename):
    '''
        securely remove the file
    '''
    removed = False
    try:
        subprocess.call('shred --remove %s' % filename, shell=True)
        removed = True
    except:
        logging.error('Unable to securely remove %s' % filename)

    if removed is False:
        try:
            os.remove(filename)
        except:
            logging.error('Unable to remove %s' % filename)


def is_secure(filename):
    '''
        Prevent shell injection
    '''
    if not(os.path.isfile(filename)):  # check if the file exist
        logging.error('%s is not a valid file' % filename)
        return False
    else:
        return True


def create_class_file(name, backup, add2archive):
    '''
        return a $FILETYPEStripper() class,
        corresponding to the filetype of the given file
    '''
    if not is_secure(name):
        return

    filename = ''
    try:
        filename = hachoir_core.cmd_line.unicodeFilename(name)
    except TypeError:  # get rid of "decoding Unicode is not supported"
        filename = name

    parser = hachoir_parser.createParser(filename)
    if not parser:
        logging.info('Unable to parse %s' % filename)
        return

    mime = parser.mime_type

    if mime.startswith('application/vnd.oasis.opendocument'):
        mime = 'application/vnd.oasis.opendocument'  # opendocument fileformat

    #stripper_class = STRIPPERS[mime]

    try:
        stripper_class = STRIPPERS[mime]
    except KeyError:
        logging.info('Don\'t have stripper for %s\'s format' % name)
        return

    return stripper_class(filename, parser, mime, backup, add2archive)
