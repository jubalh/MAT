'''
    Care about office's formats
'''

import os
import logging
import zipfile
import fileinput
import tempfile
import shutil
import xml.dom.minidom as minidom

try:
    import cairo
    from gi.repository import Poppler
except ImportError:
    logging.info('office.py loaded without PDF support')
    pass

import mat
import parser
import archive


class OpenDocumentStripper(archive.GenericArchiveStripper):
    '''
        An open document file is a zip, with xml file into.
        The one that interest us is meta.xml
    '''

    def get_meta(self):
        '''
            Return a dict with all the meta of the file by
            trying to read the meta.xml file.
        '''
        zipin = zipfile.ZipFile(self.filename, 'r')
        metadata = {}
        try:
            content = zipin.read('meta.xml')
            dom1 = minidom.parseString(content)
            elements = dom1.getElementsByTagName('office:meta')
            for i in elements[0].childNodes:
                if i.tagName != 'meta:document-statistic':
                    nodename = ''.join([k for k in i.nodeName.split(':')[1:]])
                    metadata[nodename] = ''.join([j.data for j in i.childNodes])
                else:
                    # thank you w3c for not providing a nice
                    # method to get all attributes of a node
                    pass
            zipin.close()
        except KeyError:  # no meta.xml file found
            logging.debug('%s has no opendocument metadata' % self.filename)
        return metadata

    def remove_all(self):
        '''
            FIXME ?
            There is a patch implementing the Zipfile.remove()
            method here : http://bugs.python.org/issue6818
        '''
        zipin = zipfile.ZipFile(self.filename, 'r')
        zipout = zipfile.ZipFile(self.output, 'w', allowZip64=True)

        for item in zipin.namelist():
            name = os.path.join(self.tempdir, item)
            _, ext = os.path.splitext(name)

            if item.endswith('manifest.xml'):
            # contain the list of all files present in the archive
                zipin.extract(item, self.tempdir)
                for line in fileinput.input(name, inplace=1):
                    # remove the line which contains "meta.xml"
                    line = line.strip()
                    if not 'meta.xml' in line:
                        print line
                zipout.write(name, item)

            elif ext in parser.NOMETA or item == 'mimetype':
                # keep NOMETA files, and the "manifest" file
                if item != 'meta.xml':  # contains the metadata
                    zipin.extract(item, self.tempdir)
                    zipout.write(name, item)

            else:
                zipin.extract(item, self.tempdir)
                if os.path.isfile(name):
                    try:
                        cfile = mat.create_class_file(name, False,
                            add2archive=self.add2archive)
                        cfile.remove_all()
                        logging.debug('Processing %s from %s' % (item,
                            self.filename))
                        zipout.write(name, item)
                    except:
                        logging.info('%s\'s fileformat is not supported' % item)
                        if self.add2archive:
                            zipout.write(name, item)
        zipout.comment = ''
        logging.info('%s processed' % self.filename)
        zipin.close()
        zipout.close()
        self.do_backup()
        return True

    def is_clean(self):
        '''
            Check if the file is clean from harmful metadatas
        '''
        zipin = zipfile.ZipFile(self.filename, 'r')
        try:
            zipin.getinfo('meta.xml')
        except KeyError:  # no meta.xml in the file
            czf = archive.ZipStripper(self.filename, self.parser,
                'application/zip', False, True, add2archive=self.add2archive)
            if czf.is_clean():
                zipin.close()
                return True
        zipin.close()
        return False


class PdfStripper(parser.GenericParser):
    '''
        Represent a PDF file
    '''
    def __init__(self, filename, parser, mime, backup, is_writable, **kwargs):
        super(PdfStripper, self).__init__(filename, parser, mime, backup, is_writable, **kwargs)
        uri = 'file://' + os.path.abspath(self.filename)
        self.password = None
        try:
            self.pdf_quality = kwargs['low_pdf_quality']
        except KeyError:
            self.pdf_quality = False

        self.document = Poppler.Document.new_from_file(uri, self.password)
        self.meta_list = frozenset(['title', 'author', 'subject', 'keywords', 'creator',
            'producer', 'metadata'])

    def is_clean(self):
        '''
            Check if the file is clean from harmful metadatas
        '''
        for key in self.meta_list:
            if self.document.get_property(key):
                return False
        return True

    def remove_all(self):
        '''
            Opening the PDF with poppler, then doing a render
            on a cairo pdfsurface for each pages.

            http://cairographics.org/documentation/pycairo/2/

            The use of an intermediate tempfile is necessary because
            python-cairo segfaults on unicode.
            See http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=699457
        '''
        output = tempfile.mkstemp()[1]
        page = self.document.get_page(0)
        # assume that every pages are the same size
        page_width, page_height = page.get_size()
        surface = cairo.PDFSurface(output, page_width, page_height)
        context = cairo.Context(surface)  # context draws on the surface
        logging.debug('PDF rendering of %s' % self.filename)
        for pagenum in range(self.document.get_n_pages()):
            page = self.document.get_page(pagenum)
            context.translate(0, 0)
            if self.pdf_quality:
                page.render(context)  # render the page on context
            else:
                page.render_for_printing(context)  # render the page on context
            context.show_page()  # draw context on surface
        surface.finish()
        shutil.move(output, self.output)

        try:
            import pdfrw  # For now, poppler cannot write meta, so we must use pdfrw
            logging.debug('Removing %s\'s superficial metadata' % self.filename)
            trailer = pdfrw.PdfReader(self.output)
            trailer.Info.Producer = None
            trailer.Info.Creator = None
            writer = pdfrw.PdfWriter()
            writer.trailer = trailer
            writer.write(self.output)
            self.do_backup()
        except:
            logging.error('Unable to remove all metadata from %s, please install\
pdfrw' % self.output)
            return False
        return True

    def get_meta(self):
        '''
            Return a dict with all the meta of the file
        '''
        metadata = {}
        for key in self.meta_list:
            if self.document.get_property(key):
                metadata[key] = self.document.get_property(key)
        return metadata


class OpenXmlStripper(archive.GenericArchiveStripper):
    '''
        Represent an office openxml document, which is like
        an opendocument format, with some tricky stuff added.
        It contains mostly xml, but can have media blobs, crap, ...
        (I don't like this format.)
    '''
    def remove_all(self):
        '''
            FIXME ?
            There is a patch implementing the Zipfile.remove()
            method here : http://bugs.python.org/issue6818
        '''
        zipin = zipfile.ZipFile(self.filename, 'r')
        zipout = zipfile.ZipFile(self.output, 'w',
            allowZip64=True)
        for item in zipin.namelist():
            name = os.path.join(self.tempdir, item)
            _, ext = os.path.splitext(name)
            if item.startswith('docProps/'):  # metadatas
                pass
            elif ext in parser.NOMETA or item == '.rels':
                # keep parser.NOMETA files, and the file named ".rels"
                zipin.extract(item, self.tempdir)
                zipout.write(name, item)
            else:
                zipin.extract(item, self.tempdir)
                if os.path.isfile(name):  # don't care about folders
                    try:
                        cfile = mat.create_class_file(name, False,
                            add2archive=self.add2archive)
                        cfile.remove_all()
                        logging.debug('Processing %s from %s' % (item,
                            self.filename))
                        zipout.write(name, item)
                    except:
                        logging.info('%s\'s fileformat is not supported' % item)
                        if self.add2archive:
                            zipout.write(name, item)
        zipout.comment = ''
        logging.info('%s processed' % self.filename)
        zipin.close()
        zipout.close()
        self.do_backup()
        return True

    def is_clean(self):
        '''
            Check if the file is clean from harmful metadatas
        '''
        zipin = zipfile.ZipFile(self.filename, 'r')
        for item in zipin.namelist():
            if item.startswith('docProps/'):
                return False
        zipin.close()
        czf = archive.ZipStripper(self.filename, self.parser,
                'application/zip', False, True, add2archive=self.add2archive)
        return czf.is_clean()

    def get_meta(self):
        '''
            Return a dict with all the meta of the file
        '''
        zipin = zipfile.ZipFile(self.filename, 'r')
        metadata = {}
        for item in zipin.namelist():
            if item.startswith('docProps/'):
                metadata[item] = 'harmful content'
        zipin.close()
        return metadata
