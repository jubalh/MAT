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

try:  # PDF support
    import poppler
    import cairo
    STRIPPERS['application/x-pdf'] = office.PdfStripper
    STRIPPERS['application/pdf'] = office.PdfStripper
except ImportError:
    print('Unable to import python-poppler and/or python-cairo: no PDF \
        support')

try:  # mutangen-python : audio format support
    import mutagen
    STRIPPERS['audio/x-flac'] = audio.FlacStripper
    STRIPPERS['audio/vorbis'] = audio.OggStripper
except ImportError:
    print('Unable to import python-mutagen: limited audio format support')

try:  # check if exiftool is installed on the system
    subprocess.Popen('exiftool', stdout=open('/dev/null'))
    import exiftool
    STRIPPERS['image/jpeg'] = exiftool.JpegStripper
    STRIPPERS['image/png'] = exiftool.PngStripper
except:  # if exiftool is not installed, use hachoir
    print('Unable to find exiftool: limited images support')
    STRIPPERS['image/jpeg'] = images.JpegStripper
    STRIPPERS['image/png'] = images.PngStripper

