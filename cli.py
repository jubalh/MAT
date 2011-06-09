#!/usr/bin/python
"""
    Metadata anonymisation toolkit
"""

import sys
import mat
import argparse

__version__ = "0.1"

def parsing():
    '''
	Parse the arguments,
	and returns a dict
    '''
    parser = argparse.ArgumentParser(version=__version__,
        description="Metadata Anonymisation Toolkit - CLI %s" % __version__)

    #list and check clean are mutually exclusives
    group = parser.add_mutually_exclusive_group()

    #list meta
    group.add_argument('--print-meta', '-p', action="store_true", default=False,
        dest='just_list', help='List all the meta of a file,\
        without removing them')

    #check if the file is clean
    group.add_argument('--check-clean', '-c', action="store_true",
        default=False, dest='just_check',
        help='Check if a file is clean of harmfull metadatas')

    #list of files to process
    parser.add_argument('filelist', action="store", type=str, nargs="+",
        metavar='file', help='File(s) to process')

    return parser.parse_args()

def list_meta(class_file, filename):
    '''
	Print all the meta of "filename" on stdout
    '''
    print("[+] File %s :" % filename)
    for key, item in class_file.get_meta().iteritems():
        print("\t%s : %s" % (key, item) )

def is_clean(class_file, filename):
    '''
	Say if "filename" is clean or not
    '''
    if class_file.is_clean():
        print("[+] %s is clean" % filename)
    else:
        print("[+] %s is not clean" % filename)

def clean_meta(class_file, filename):
    '''
	Clean the file "filename"
    '''
    print("[+] Cleaning %s" % filename)
    if class_file.is_clean():
        print("%s is already clean" % filename)
    else:
        class_file.remove_all()
        print("%s cleaned !" % filename)

def main():
    args = parsing()

    #func receive the function correponding to the options given as parameters
    if args.just_list is True: #only print metadatas
        func = list_meta
    elif args.just_check is True: #only check if the file is clean
        func = is_clean
    else: #clean the file
        func = clean_meta

    for filename in args.filelist:
        class_file = mat.create_class_file(filename)
        func(class_file, filename)
        print("\n")

if __name__ == '__main__':
    main()
