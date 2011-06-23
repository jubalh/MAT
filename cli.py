#!/usr/bin/python
'''
    Metadata anonymisation toolkit - CLI edition
'''

import sys
from lib import mat
import optparse

__version__ = '0.1'

def parse():
    parser = optparse.OptionParser(usage='%prog [options] filename')
    common = optparse.OptionGroup(parser, 'Metadata Anonymisation Toolkit - CLI')
    common.add_option('--display', '-d', action='store_true', default=False,
        help='List all the meta of a file without removing them')
    common.add_option('--check', '-c',  action='store_true', default=False,
        help='Check if a file is free of harmfull metadatas')
    common.add_option('--version', action='callback', callback=displayVersion,
        help='Display version and exit')

    parser.add_option_group(common)

    values, arguments = parser.parse_args()
    if not arguments:
        parser.print_help()
        sys.exit(1)
    return values, arguments

def displayVersion():
    print('Metadata Anonymisation Toolkit - CLI %s') % __version__
    print('Hachoir library version %s') % hachoir_core.__version__
    sys.exit(0)

def list_meta(class_file, filename):
    '''
	Print all the meta of 'filename' on stdout
    '''
    print('[+] File %s :' % filename)
    for key, value in class_file.get_meta().iteritems():
        print key + ' : ' + value

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

def main():
    args, filenames = parse()

    #func receive the function correponding to the options given as parameters
    if args.display is True: #only print metadatas
        func = list_meta
    elif args.check is True: #only check if the file is clean
        func = is_clean
    else: #clean the file
        func = clean_meta

    for filename in filenames:
        class_file = mat.create_class_file(filename)
        func(class_file, filename)
        print('\n')

if __name__ == '__main__':
    main()
