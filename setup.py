#!/usr/bin/env python

from distutils.core import setup

setup(name='MAT',
      version='0.1',
      description='Metadata Anonymisation Toolkit',
      author='Julien (jvoisin) Voisin',
      author_email='julien.voisin@dustri.org',
      license='GPLv2',
      url='https://gitweb.torproject.org/user/jvoisin/mat.git',
      packages=['mat', 'mat.hachoir_editor', 'mat.pdfrw', 'mat.bencode', 'mat.tarfile'],
      scripts=['mat-cli', 'mat-gui'],
      data_files=[
          ( '/usr/share/applications/', [ 'mat.desktop' ] ),
          ( '', ['FORMATS'] ),
          ]
     )
