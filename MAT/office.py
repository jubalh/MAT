''' Care about office's formats
'''

import logging
import os
import shutil
import tempfile
import xml.dom.minidom as minidom
import zipfile

try:
    import cairo
    from gi.repository import Poppler
except ImportError:
    logging.info('office.py loaded without PDF support')
    pass

import parser
import archive


class OpenDocumentStripper(archive.ZipStripper):
    ''' An open document file is a zip, with xml file into.
        The one that interest us is meta.xml
    '''

    def get_meta(self):
        ''' Return a dict with all the meta of the file by
            trying to read the meta.xml file.
        '''
        metadata = super(OpenDocumentStripper, self).get_meta()
        zipin = zipfile.ZipFile(self.filename, 'r')
        try:
            content = zipin.read('meta.xml')
            dom1 = minidom.parseString(content)
            elements = dom1.getElementsByTagName('office:meta')
            for i in elements[0].childNodes:
                if i.tagName != 'meta:document-statistic':
                    nodename = ''.join(i.nodeName.split(':')[1:])
                    metadata[nodename] = ''.join([j.data for j in i.childNodes])
                else:
                    # thank you w3c for not providing a nice
                    # method to get all attributes of a node
                    pass
        except KeyError:  # no meta.xml file found
            logging.debug('%s has no opendocument metadata' % self.filename)
        zipin.close()
        return metadata

    def remove_all(self):
        ''' Removes metadata
        '''
        return super(OpenDocumentStripper, self).remove_all(ending_blacklist=['meta.xml'])

    def is_clean(self):
        ''' Check if the file is clean from harmful metadatas
        '''
        clean_super = super(OpenDocumentStripper, self).is_clean()
        if clean_super is False:
            return False

        zipin = zipfile.ZipFile(self.filename, 'r')
        try:
            zipin.getinfo('meta.xml')
        except KeyError:  # no meta.xml in the file
            return True
        zipin.close()
        return False


class OpenXmlStripper(archive.ZipStripper):
    ''' Represent an office openxml document, which is like
        an opendocument format, with some tricky stuff added.
        It contains mostly xml, but can have media blobs, crap, ...
        (I don't like this format.)
    '''
    def remove_all(self):
        return super(OpenXmlStripper, self).remove_all(
                beginning_blacklist=('docProps/'), whitelist=('.rels'))

    def is_clean(self):
        ''' Check if the file is clean from harmful metadatas.
            This implementation is faster than something like
            "return this.get_meta() == {}".
        '''
        clean_super = super(OpenXmlStripper, self).is_clean()
        if clean_super is False:
            return False

        zipin = zipfile.ZipFile(self.filename, 'r')
        for item in zipin.namelist():
            if item.startswith('docProps/'):
                return False
        zipin.close()
        return True

    def get_meta(self):
        ''' Return a dict with all the meta of the file
        '''
        metadata = super(OpenXmlStripper, self).get_meta()

        zipin = zipfile.ZipFile(self.filename, 'r')
        for item in zipin.namelist():
            if item.startswith('docProps/'):
                metadata[item] = 'harmful content'
        zipin.close()
        return metadata


class PdfStripper(parser.GenericParser):
    ''' Represent a PDF file
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
        self.meta_list = frozenset(['title', 'author', 'subject',
            'keywords', 'creator', 'producer', 'metadata'])

    def is_clean(self):
        ''' Check if the file is clean from harmful metadatas
        '''
        for key in self.meta_list:
            if self.document.get_property(key):
                return False
        return True

    def remove_all(self):
        ''' Opening the PDF with poppler, then doing a render
            on a cairo pdfsurface for each pages.

            http://cairographics.org/documentation/pycairo/2/

            The use of an intermediate tempfile is necessary because
            python-cairo segfaults on unicode.
            See http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=699457
        '''
        try:
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
        except:
            logging.error('Something went wrong when cleaning %s.' % self.filename)
            return False

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
            logging.error('Unable to remove all metadata from %s, please install pdfrw' % self.output)
            return False
        return True

    def get_meta(self):
        ''' Return a dict with all the meta of the file
        '''
        metadata = {}
        for key in self.meta_list:
            if self.document.get_property(key):
                metadata[key] = self.document.get_property(key)
        return metadata
