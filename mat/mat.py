#!/usr/bin/env python

'''
    Metadata anonymisation toolkit library
'''

import os
import subprocess
import logging
import mimetypes
import xml.sax

import hachoir_core.cmd_line
import hachoir_parser

import images
import audio
import office
import archive
import misc

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
    'application/x-bittorrent': misc.TorrentStripper,
    'application/opendocument': office.OpenDocumentStripper,
    'application/officeopenxml': office.OpenXmlStripper,
}

try:
    import poppler
    import cairo
    STRIPPERS['application/x-pdf'] = office.PdfStripper
    STRIPPERS['application/pdf'] = office.PdfStripper
except ImportError:
    print('Unable to import python-poppler and/or python-cairo: no pdf \
        support')

try:
    import mutagen
    STRIPPERS['audio/x-flac'] = audio.FlacStripper
    STRIPPERS['audio/vorbis'] = audio.OggStripper
except ImportError:
    print('Unable to import python-mutagen: limited audio format support')

try:
    #FIXME : WIP
    subprocess.Popen('exiftool_', stdout=open('/dev/null'))
    import exiftool
    #STRIPPERS['image/jpeg'] = exiftool.JpegStripper
    #STRIPPERS['image/png'] = exiftool.PngStripper
except:
    #print('Unable to find exiftool: limited images support')
    STRIPPERS['image/jpeg'] = images.JpegStripper
    STRIPPERS['image/png'] = images.PngStripper


def get_sharedir():
    '''
        An ugly hack to find where is the "FORMATS" file.
    '''
    if os.path.isfile('FORMATS'):
        return ''
    elif os.path.exists('/usr/local/share/mat/'):
        return '/usr/local/share/mat/'


class XMLParser(xml.sax.handler.ContentHandler):
    '''
        Parse the supported format xml, and return a corresponding
        list of dict
    '''
    def __init__(self):
        self.dict = {}
        self.list = []
        self.content, self.key = '', ''
        self.between = False

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
            content = self.content.replace('\s', ' ')
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
        subprocess.call(['shred', '--remove', filename])
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

    if mime == 'application/zip':  # some formats are zipped stuff
        mime = mimetypes.guess_type(name)[0]

    if mime.startswith('application/vnd.oasis.opendocument'):
        mime = 'application/opendocument'  # opendocument fileformat
    elif mime.startswith('application/vnd.openxmlformats-officedocument'):
        mime = 'application/officeopenxml'  # office openxml

    try:
        stripper_class = STRIPPERS[mime]
    except KeyError:
        logging.info('Don\'t have stripper for %s format' % mime)
        return

    return stripper_class(filename, parser, mime, backup, add2archive)
