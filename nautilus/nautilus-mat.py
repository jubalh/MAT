#! /usr/bin/python

import os
import urllib
import logging
try:
    import gettext
    gettext.install("mat")
except:
    logging.warning("Failed to initialise gettext")
    _ = lambda x: x

import xml.sax

from gi.repository import Nautilus, GObject, Gtk

import MAT.mat
import MAT.strippers

class MatExtension(GObject.GObject, Nautilus.MenuProvider):
    def __init__(self):
        logging.debug("nautilus-mat: initialising")
        pass

    def get_file_items(self, window, files):
        if len(files) != 1:
            return

        file = files[0]

        # We're only going to put ourselves on supported mimetypes' context menus
        if not (file.get_mime_type()
                in [i["mimetype"] for i in MAT.mat.list_supported_formats()]):
            logging.debug("%s is not supported by MAT" % file.get_mime_type())
            return

        # MAT can only handle local file:
        if file.get_uri_scheme() != 'file':
            logging.debug("%s files not supported by MAT" % file.get_uri_scheme())
            return

        item = Nautilus.MenuItem(name="Nautilus::clean_metadata",
                                 label=_("Clean metadata"),
                                 tip=_("Clean file's metadata with MAT"),
                                 icon="gtk-clear")
        item.connect('activate', self.menu_activate_cb, file)
        return item,

    def show_message(self, message, type = Gtk.MessageType.INFO):
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


