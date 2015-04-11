METADATA
========
Metadata consist of information that characterizes data.
Metadata are used to provide documentation for data products.
In essence, metadata answer who, what, when, where, why, and how about
every facet of the data that are being documented.

METADATA AND PRIVACY
====================
Metadata within a file can tell a lot about you.
Cameras record data about when a picture was taken and what
camera was used. Office documents like PDF or Office automatically adds
author and company information to documents and spreadsheets.
Maybe you don't want to disclose those information on the web.

WARNINGS
========
See README.security

DEPENDENCIES
============
 * python2.7 (at least)
 * python-hachoir-core and python-hachoir-parser
 * python-pil for more secure images handling
 * python-pdfrw, gir-poppler and python-gi-cairo for full PDF support
 * python-gi for the GUI
 * shred (should be already installed)

OPTIONALS DEPENDENCIES
======================
 * python-mutagen: for massive audio format support
 * exiftool: for _massive_ image format support

USAGE
=====
    mat --help
or

    mat-gui

SUPPORTED FORMAT
================
See ./data/FORMATS

HOW TO IMPLEMENT NEW FORMATS
============================
1. Add the format's mimetype to the STRIPPER list in strippers.py
2. Inherit the GenericParser class (parser.py)
3. Read the parser.py module
4. Implement at least these three methods:
    - is_clean(self)
    - remove_all(self)
    - get_meta(self)
5. Don't forget to call the do_backup() method when necessary

HOW TO LAUNCH THE TESTSUITE
===========================
    cd ./test
    python test.py

LINKS
=====
* Official website: https://mat.boum.org
* Bugtracker: https://labs.riseup.net/code/projects/mat
* Git repo: https://gitweb.torproject.org/user/jvoisin/mat.git

CONTACT
=======
If you have question, patches, bug reports, or simply want to talk about this project,
please use the mailing list (https://mailman.boum.org/listinfo/mat-dev).
You can also contact contact jvoisin
on irc.oftc.net or at julien.voisin@dustri.org.

LICENSE
=======
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2 as
published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
MA 02110-1301, USA.

Copyright 2011-2015 Julien (jvoisin) Voisin <julien.voisin@dustri.org>


THANKS
======
Mat would not exist without :

 * the Google Summer of Code,
 * the hachoir library,
 * people on #tails@oftc

Many thanks to them !
