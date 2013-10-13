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

import MAT.exceptions

__version__ = '0.4'
__author__ = 'jvoisin'

#Silence
LOGGING_LEVEL = logging.CRITICAL
hachoir_core.config.quiet = True
fname = ''

#Verbose
#LOGGING_LEVEL = logging.DEBUG
#hachoir_core.config.quiet = False
#logname = 'report.log'

logging.basicConfig(filename=fname, level=LOGGING_LEVEL)

import strippers  # this is loaded here because we need LOGGING_LEVEL

def get_logo():
    if os.path.isfile('./data/mat.png'):
        return './data/mat.png'
    elif os.path.isfile('/usr/share/pixmaps/mat.png'):
        return '/usr/share/pixmaps/mat.png'
    elif os.path.isfile('/usr/local/share/pixmaps/mat.png'):
        return '/usr/local/share/pixmaps/mat.png'

def get_datadir():
    if os.path.isdir('./data/'):
        return './data/'
    elif os.path.isdir('/usr/local/share/mat/'):
        return '/usr/local/share/mat/'
    elif os.path.isdir('/usr/share/mat/'):
        return '/usr/share/mat/'

def list_supported_formats():
    '''
        Return a list of all locally supported fileformat
    '''
    handler = XMLParser()
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)
    path = os.path.join(get_datadir(), 'FORMATS')
    with open(path, 'r') as xmlfile:
        parser.parse(xmlfile)

    localy_supported = []
    for item in handler.list:
        if strippers.STRIPPERS.has_key(item['mimetype'].split(',')[0]):
            localy_supported.append(item)

    return localy_supported

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
            Called when entering into xml tag
        '''
        self.between = True
        self.key = name
        self.content = ''

    def endElement(self, name):
        '''
            Called when exiting a xml tag
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
            Concatenate the content between opening and closing tags
        '''
        if self.between:
            self.content += characters


def secure_remove(filename):
    '''
        securely remove the file
    '''
    try:
        if subprocess.call(['shred', '--remove', filename]) == 0:
            return True
        else:
            raise OSError
    except OSError:
        logging.error('Unable to securely remove %s' % filename)

    try:
        os.remove(filename)
        return True
    except OSError:
        logging.error('Unable to remove %s' % filename)
        raise MAT.exceptions.UnableToRemoveFile


def create_class_file(name, backup, **kwargs):
    '''
        return a $FILETYPEStripper() class,
        corresponding to the filetype of the given file
    '''
    if not os.path.isfile(name):
        # check if the file exists
        logging.error('%s is not a valid file' % name)
        return None

    if not os.access(name, os.R_OK):
        #check read permissions
        logging.error('%s is is not readable' % name)
        return None

    is_writable = os.access(name, os.W_OK)

    if not os.path.getsize(name):
        #check if the file is not empty (hachoir crash on empty files)
        logging.error('%s is empty' % name)
        return None

    filename = ''
    try:
        filename = hachoir_core.cmd_line.unicodeFilename(name)
    except TypeError:  # get rid of "decoding Unicode is not supported"
        filename = name

    parser = hachoir_parser.createParser(filename)
    if not parser:
        logging.info('Unable to parse %s' % filename)
        return None

    mime = parser.mime_type

    if mime == 'application/zip':  # some formats are zipped stuff
        if mimetypes.guess_type(name)[0] is not None:
            mime =  mimetypes.guess_type(name)[0]

    if mime.startswith('application/vnd.oasis.opendocument'):
        mime = 'application/opendocument'  # opendocument fileformat
    elif mime.startswith('application/vnd.openxmlformats-officedocument'):
        mime = 'application/officeopenxml'  # office openxml

    try:
        stripper_class = strippers.STRIPPERS[mime]
    except KeyError:
        logging.info('Don\'t have stripper for %s format' % mime)
        return None

    return stripper_class(filename, parser, mime, backup, is_writable, **kwargs)
