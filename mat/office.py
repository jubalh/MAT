'''
    Care about office's formats
'''

import os
import logging
import zipfile
import fileinput
import subprocess
import xml.dom.minidom as minidom

try:
    import cairo
    import poppler
except ImportError:
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
                    # method to get all attributes from a node
                    pass
            zipin.close()
        except KeyError:  # no meta.xml file found
            logging.debug('%s has no opendocument metadata' % self.filename)
        return metadata

    def _remove_all(self, method):
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
                    #remove the line which contains "meta.xml"
                    line = line.strip()
                    if not 'meta.xml' in line:
                        print line
                zipout.write(name, item)

            elif ext in parser.NOMETA or item == 'mimetype':
                #keep NOMETA files, and the "manifest" file
                if item != 'meta.xml':  # contains the metadata
                    zipin.extract(item, self.tempdir)
                    zipout.write(name, item)

            else:
                zipin.extract(item, self.tempdir)
                if os.path.isfile(name):
                    try:
                        cfile = mat.create_class_file(name, False,
                            self.add2archive)
                        if method == 'normal':
                            cfile.remove_all()
                        else:
                            cfile.remove_all_strict()
                        logging.debug('Processing %s from %s' % (item,
                            self.filename))
                        zipout.write(name, item)
                    except:
                        logging.info('%s\' fileformat is not supported' % item)
                        if self.add2archive:
                            zipout.write(name, item)
        zipout.comment = ''
        logging.info('%s treated' % self.filename)
        zipin.close()
        zipout.close()
        self.do_backup()
        self.set_time(archive.ZIP_TIME)
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
                'application/zip', self.backup, self.add2archive)
            if czf.is_clean():
                zipin.close()
                return True
        zipin.close()
        return False


class PdfStripper(parser.GenericParser):
    '''
        Represent a PDF file
    '''
    def __init__(self, filename, parser, mime, backup, add2archive):
        super(PdfStripper, self).__init__(filename, parser, mime, backup,
            add2archive)
        uri = 'file://' + os.path.abspath(self.filename)
        self.password = None
        self.document = poppler.document_new_from_file(uri, self.password)
        self.meta_list = ('title', 'author', 'subject', 'keywords', 'creator',
            'producer', 'metadata')

    def is_clean(self):
        '''
            Check if the file is clean from harmful metadatas
        '''
        for key in self.meta_list:
            if self.document.get_property(key) is not None and \
                self.document.get_property(key) != '':
                return False
        return True


    def remove_all(self):
        '''
            Remove supperficial
        '''
        return self._remove_meta()


    def remove_all_strict(self):
        '''
            Opening the PDF with poppler, then doing a render
            on a cairo pdfsurface for each pages.
            Thanks to Lunar^for the idea.
            http://cairographics.org/documentation/pycairo/2/
            python-poppler is not documented at all : have fun ;)
        '''
        page = self.document.get_page(0)
        page_width, page_height = page.get_size()
        surface = cairo.PDFSurface(self.output, page_width, page_height)
        context = cairo.Context(surface)  # context draws on the surface
        logging.debug('PDF rendering of %s' % self.filename)
        for pagenum in xrange(self.document.get_n_pages()):
            page = self.document.get_page(pagenum)
            context.translate(0, 0)
            page.render(context)  # render the page on context
            context.show_page()  # draw context on surface
        surface.finish()
        return self._remove_meta()

    def _remove_meta(self):
        '''
            Remove superficial/external metadata
            from a PDF file, using exiftool,
            of pdfrw if exiftool is not installed
        '''
        processed = False
        try:# try with pdfrw
            import pdfrw
            #For now, poppler cannot write meta, so we must use pdfrw
            logging.debug('Removing %s\'s superficial metadata' % self.filename)
            trailer = pdfrw.PdfReader(self.output)
            trailer.Info.Producer = trailer.Author = trailer.Info.Creator = None
            writer = pdfrw.PdfWriter()
            writer.trailer = trailer
            writer.write(self.output)
            self.do_backup()
            processed = True
        except:
            pass

        try:  # try with exiftool
            subprocess.Popen('exiftool', stdout=open('/dev/null'))
            import exiftool
            # Note: '-All=' must be followed by a known exiftool option.
            if self.backup:
                process = subprocess.Popen(['exiftool', '-m', '-All=',
                    '-out', self.output, self.filename], stdout=open('/dev/null'))
                process.wait()
            else:
                # Note: '-All=' must be followed by a known exiftool option.
                process = subprocess.Popen(
                    ['exiftool', '-All=', '-overwrite_original', self.filename],
                    stdout=open('/dev/null'))
                process.wait()
            processed = True
        except:
            pass

        if processed is False:
            logging.error('Please install either pdfrw, or exiftool to\
                    fully handle PDF files')

        self.set_time(parser.EPOCH)
        return processed

    def get_meta(self):
        '''
            Return a dict with all the meta of the file
        '''
        metadata = {}
        for key in self.meta_list:
            if self.document.get_property(key) is not None and \
                self.document.get_property(key) != '':
                metadata[key] = self.document.get_property(key)
        return metadata


class OpenXmlStripper(archive.GenericArchiveStripper):
    '''
        Represent an office openxml document, which is like
        an opendocument format, with some tricky stuff added.
        It contains mostly xml, but can have media blobs, crap, ...
        (I don't like this format.)
    '''
    def _remove_all(self, method):
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
                #keep parser.NOMETA files, and the file named ".rels"
                zipin.extract(item, self.tempdir)
                zipout.write(name, item)
            else:
                zipin.extract(item, self.tempdir)
                if os.path.isfile(name):  # don't care about folders
                    try:
                        cfile = mat.create_class_file(name, False,
                            self.add2archive)
                        if method == 'normal':
                            cfile.remove_all()
                        else:
                            cfile.remove_all_strict()
                        logging.debug('Processing %s from %s' % (item,
                            self.filename))
                        zipout.write(name, item)
                    except:
                        logging.info('%s\' fileformat is not supported' % item)
                        if self.add2archive:
                            zipout.write(name, item)
        zipout.comment = ''
        logging.info('%s treated' % self.filename)
        zipin.close()
        zipout.close()
        self.do_backup()
        self.set_time(archive.ZIP_TIME)
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
                'application/zip', self.backup, self.add2archive)
        if not czf.is_clean():
            return False
        else:
            return True

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
