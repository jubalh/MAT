#!/usr/bin/env python

import os
import sys
import glob
import subprocess

from distutils.core import setup

from lib import mat

#Remove MANIFEST file, since distutils
#doesn't properly update it when
#the contents of directories changes.
if os.path.exists('MANIFEST'):
    os.remove('MANIFEST')


def l10n():
    '''
        Compile .po files to .mo
    '''
    for language in glob.glob('locale/*/'):
        fpath = os.path.join(language, 'LC_MESSAGES', 'mat-gui.po')
        output = fpath[:-2] + 'mo'
        subprocess.call(['msgfmt', fpath, '-o', output])
        yield output

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
        ( 'share/mat/locale/', [i for i in l10n()] ),
    ],
)
