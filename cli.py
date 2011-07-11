#!/usr/bin/python
'''
    Metadata anonymisation toolkit - CLI edition
'''

import sys
from lib import mat
import argparse
import hachoir_core

__version__ = '0.1'

def parse():
    parser = argparse.ArgumentParser(version=__version__,
        description="Metadata Anonymisation Toolkit - CLI %s" % __version__)

    #list and check clean are mutually exclusives
    group = parser.add_mutually_exclusive_group()

    group.add_argument('--display', '-d', action='store_true', default=False,
        dest='display', help='List all the meta of a file')
    group.add_argument('--check', '-c',  action='store_true', default=False,
        dest='check', help='Check if a file is free of harmfull metadatas')

    parser.add_argument('--backup', '-b', action='store_true', default=False,
        dest='backup', help='Keep a backup copy')
    parser.add_argument('--ugly', '-u', action='store_true', default=False,
        dest='ugly', help='Remove harmful meta but information loss may occure')
    parser.add_argument('filelist', action='store', type=str, nargs='+',
        metavar='files', help='File(s) to process')

    return parser.parse_args()

def list_meta(class_file, filename):
    '''
	Print all the meta of 'filename' on stdout
    '''
    print('[+] File %s :' % filename)
    if class_file.is_clean():
        print('No harmful meta found')
    else:
        for key, value in class_file.get_meta().iteritems():
            print(key + ' : ' + str(value))

def is_clean(class_file, filename):
    '''
	Say if 'filename' is clean or not
    '''
    if class_file.is_clean():
        print('[+] %s is clean' % filename)
    else:
        print('[+] %s is not clean' % filename)

def clean_meta(class_file, filename):
    '''
	Clean the file 'filename'
    '''
    print('[+] Cleaning %s' % filename)
    if class_file.is_clean():
        print('%s is already clean' % filename)
    else:
        class_file.remove_all()
        print('%s cleaned !' % filename)

def clean_meta_ugly(class_file, filename):
    '''
	Clean the file 'filename', ugly way
    '''
    print('[+] Cleaning %s' % filename)
    if class_file.is_clean():
        print('%s is already clean' % filename)
    else:
        class_file.remove_all_ugly()
        print('%s cleaned' % filename)

def main():
    args = parse()

    #func receive the function correponding to the options given as parameters
    if args.display is True: #only print metadatas
        func = list_meta
    elif args.check is True: #only check if the file is clean
        func = is_clean
    elif args.ugly is True: #destructive anonymisation method
        func = clean_meta_ugly
    else: #clean the file
        func = clean_meta

    for filename in args.filelist:
        class_file = mat.create_class_file(filename, args.backup)
        if class_file is not None:
            func(class_file, filename)

if __name__ == '__main__':
    main()
