#! /usr/bin/python

''' This file is an extension for the Nautilus
    file manager, to provide a contextual menu to
    clean metadata
'''

import logging
import urllib
try:
    import gettext
    gettext.install("mat")
except:
    logging.warning("Failed to initialise gettext")
    _ = lambda x: x

from gi.repository import Nautilus, GObject, Gtk

import MAT.mat
import MAT.strippers


class MatExtension(GObject.GObject, Nautilus.MenuProvider):
    def __init__(self):
        logging.debug("nautilus-mat: initialising")
        pass

    def get_file_items(self, window, files):
        if len(files) != 1:  # no multi-files support
            return

        file = files.pop()

        # We're only going to put ourselves on supported mimetypes' context menus
        if not (file.get_mime_type()
                in [i["mimetype"] for i in MAT.mat.list_supported_formats()]):
            logging.debug("%s is not supported by MAT" % file.get_mime_type())
            return

        # MAT can only handle local file:
        if file.get_uri_scheme() != 'file':
            logging.debug("%s files not supported by MAT" % file.get_uri_scheme())
            return

        # MAT can not clean non-writable files
        if not file.can_write():
            logging.debug("%s is not writable by MAT" % file.get_uri_scheme())
            return

        item = Nautilus.MenuItem(name="Nautilus::clean_metadata",
                                 label=_("Clean metadata"),
                                 tip=_("Clean file's metadata with MAT"),
                                 icon="gtk-clear")
        item.connect('activate', self.menu_activate_cb, file)
        return item,

    def show_message(self, message, type=Gtk.MessageType.INFO):
        dialog = Gtk.MessageDialog(parent=None,
                                   flags=Gtk.DialogFlags.MODAL,
                                   type=type,
                                   buttons=Gtk.ButtonsType.OK,
                                   message_format=message)
        ret = dialog.run()
        dialog.destroy()
        return ret

    def menu_activate_cb(self, menu, file):
        if file.is_gone():
            return

        file_path = urllib.unquote(file.get_uri()[7:])

        class_file = MAT.mat.create_class_file(file_path,
                                           backup=True,
                                           add2archive=False)
        if class_file:
            if class_file.is_clean():
                self.show_message(_("%s is already clean") % file_path)
            else:
                if not class_file.remove_all():
                    self.show_message(_("Unable to clean %s") % file_path, Gtk.MessageType.ERROR)
        else:
            self.show_message(_("Unable to process %s") % file_path, Gtk.MessageType.ERROR)
