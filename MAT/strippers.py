'''
    Manage which fileformat can be processed
'''

import images
import audio
import office
import archive
import misc
import subprocess

STRIPPERS = {
    'application/x-tar': archive.TarStripper,
    'application/x-gzip': archive.GzipStripper,
    'application/x-bzip2': archive.Bzip2Stripper,
    'application/zip': archive.ZipStripper,
    'audio/mpeg': audio.MpegAudioStripper,
    'application/x-bittorrent': misc.TorrentStripper,
    'application/opendocument': office.OpenDocumentStripper,
    'application/officeopenxml': office.OpenXmlStripper,
}


# PDF support
pdfSupport = True
try:
    import poppler
except ImportError:
    print('Unable to import python-poppler: not PDF support')
    pdfSupport = False

try:
    import cairo
except ImportError:
    print('Unable to import python-cairo: no PDF support')
    pdfSupport = False

try:
    import pdfrw
except ImportError:
    print('Unable to import python-pdfrw: no PDf support')
    pdfSupport = False

if pdfSupport:
    STRIPPERS['application/x-pdf'] = office.PdfStripper
    STRIPPERS['application/pdf'] = office.PdfStripper


# audio format support with mutagen-python
try:
    import mutagen
    STRIPPERS['audio/x-flac'] = audio.FlacStripper
    STRIPPERS['audio/vorbis'] = audio.OggStripper
except ImportError:
    print('Unable to import python-mutagen: limited audio format support')

# exiftool
try:
    subprocess.Popen('exiftool', stdout=open('/dev/null'))
    import exiftool
    STRIPPERS['image/jpeg'] = exiftool.JpegStripper
    STRIPPERS['image/png'] = exiftool.PngStripper
except:  # if exiftool is not installed, use hachoir
    print('Unable to find exiftool: limited images support')
    STRIPPERS['image/jpeg'] = images.JpegStripper
    STRIPPERS['image/png'] = images.PngStripper

