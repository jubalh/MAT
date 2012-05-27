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

import strippers

__version__ = '0.3.2'
__author__ = 'jvoisin'

#Silence
LOGGING_LEVEL = logging.CRITICAL
hachoir_core.config.quiet = True
fname = ''

#Verbose
LOGGING_LEVEL = logging.DEBUG
#hachoir_core.config.quiet = False
#logname = 'report.log'

logging.basicConfig(filename=fname, level=LOGGING_LEVEL)


def get_sharedir(filename):
    '''
        An ugly hack to find various files
    '''
    if os.path.isfile(filename):
        return filename
    elif os.path.exists(os.path.join('/usr/local/share/mat/', filename)):
        return os.path.join('/usr/local/share/mat/', filename)
    elif os.path.exists(os.path.join('/usr/share/mat/', filename)):
        return os.path.join('/usr/share/mat', filename)


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
        if self.between:
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


def create_class_file(name, backup, add2archive):
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

    if not os.access(name, os.W_OK):
        #check write permission
        logging.error('%s is not writtable' % name)
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
        mime = mimetypes.guess_type(name)[0]

    if mime.startswith('application/vnd.oasis.opendocument'):
        mime = 'application/opendocument'  # opendocument fileformat
    elif mime.startswith('application/vnd.openxmlformats-officedocument'):
        mime = 'application/officeopenxml'  # office openxml

    try:
        stripper_class = strippers.STRIPPERS[mime]
    except KeyError:
        logging.info('Don\'t have stripper for %s format' % mime)
        return None

    return stripper_class(filename, parser, mime, backup, add2archive)
