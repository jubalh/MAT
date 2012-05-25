#!/usr/bin/env python

import os

from distutils.core import setup
from DistUtilsExtra.command import *

from lib import mat

#Remove MANIFEST file, since distutils
#doesn't properly update it when
#the contents of directories changes.
if os.path.exists('MANIFEST'):
    os.remove('MANIFEST')

setup(
    name              = 'MAT',
    version           = mat.__version__,
    description       = 'Metadata Anonymisation Toolkit',
    long_description  = 'A Metadata Anonymisation Toolkit in Python, using python-hachoir',
    author            = mat.__author__,
    author_email      = 'julien.voisin@dustri.org',
    platforms         = 'linux',
    license           = 'GPLv2',
    url               = 'https://mat.boum.org',
    packages          = ['lib', 'lib.hachoir_editor', 'lib.bencode', 'lib.tarfile'],
    scripts           = ['mat', 'mat-gui'],
    data_files        = [
        ( 'share/applications', ['mat.desktop'] ),
        ( 'share/mat', ['FORMATS', 'logo.png'] ),
        ( 'share/doc/mat', ['README', 'TODO'] ),
    ],
    cmdclass          = {
        'build': build_extra.build_extra,
        'build_i18n': build_i18n.build_i18n,
        'build_help': build_help.build_help,
        'build_icons': build_icons.build_icons,
        'clean': clean_i18n.clean_i18n,
    },
)
