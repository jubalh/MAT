#!/usr/bin/env python

import os

from distutils.core import setup

from mat import mat

#Remove MANIFEST file, since distutils
#doesn't properly update it when
#the contents of directories changes.
if os.path.exists('MANIFEST'):
    os.remove('MANIFEST')

setup(
    name              = 'MAT',
    version           = mat.__version__,
    description       = 'Metadata Anonymisation Toolkit',
    long_decription   = 'A Metadata Anonymisation Toolkit in Python, using python-hachoir',
    author            = mat.__author__,
    author_email      = 'julien.voisin@dustri.org',
    plateforms        = 'linux',
    license           = 'GPLv2',
    url               = 'https://mat.boum.org',
    packages          = ['mat', 'mat.hachoir_editor', 'mat.bencode', 'mat.tarfile'],
    scripts           = ['mat-cli', 'mat-gui'],
    data_files        = [
        ( 'share/applications', [ 'mat.desktop' ] ),
        ( 'share/mat', ['FORMATS'] ),
        ( 'share/doc/mat', ['README', 'TODO'] ),
    ],
)
