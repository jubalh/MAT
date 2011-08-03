#!/usr/bin/env python

'''
    Metadata anonymisation toolkit - GUI edition
'''

import gtk
import gobject

import os
import logging
import xml.sax

from lib import mat

__version__ = '0.1'
__author__ = 'jvoisin'

logging.basicConfig(level=mat.LOGGING_LEVEL)


class CFile(gobject.GObject):
    '''
        Contain the class-file of the file "path"
        This class exist just to be "around" my parser.Generic_parser class,
        since gtk.ListStore does not accept it.
    '''
    def __init__(self, path, backup, add2archive):
        gobject.GObject.__init__(self)
        try:
            self.file = mat.create_class_file(path, backup, add2archive)
        except:
            self.file = None


class ListStoreApp:
    '''
        Main GUI class
    '''
    def __init__(self):
        # Preferences
        self.add2archive = True
        self.backup = True
        self.force = False

        self.window = gtk.Window()
        self.window.set_title('Metadata Anonymisation Toolkit %s' %
            __version__)
        self.window.connect('destroy', gtk.main_quit)
        self.window.set_default_size(800, 600)

        vbox = gtk.VBox()
        self.window.add(vbox)

        menubar = self.create_menu()
        toolbar = self.create_toolbar()
        content = gtk.ScrolledWindow()
        vbox.pack_start(menubar, False, True, 0)
        vbox.pack_start(toolbar, False, True, 0)
        vbox.pack_start(content, True, True, 0)

        # parser.class - name - type - cleaned
        self.liststore = gtk.ListStore(CFile, str, str, str)

        treeview = gtk.TreeView(model=self.liststore)
        treeview.set_search_column(1)  # name column is searchable
        treeview.set_rules_hint(True)  # alternate colors for rows
        treeview.set_rubber_banding(True)  # mouse selection
        self.add_columns(treeview)
        self.selection = treeview.get_selection()
        self.selection.set_mode(gtk.SELECTION_MULTIPLE)

        content.add(treeview)

        self.statusbar = gtk.Statusbar()
        self.statusbar.push(1, 'Ready')
        vbox.pack_start(self.statusbar, False, False, 0)

        self.window.show_all()

    def create_toolbar(self):
        '''
            Returns a vbox object, which contains a toolbar with buttons
        '''
        toolbar = gtk.Toolbar()

        toolbutton = gtk.ToolButton(gtk.STOCK_ADD)
        toolbutton.set_label('Add')
        toolbutton.connect('clicked', self.add_files)
        toolbutton.set_tooltip_text('Add files')
        toolbar.add(toolbutton)

        toolbutton = gtk.ToolButton(gtk.STOCK_PRINT_REPORT)
        toolbutton.set_label('Clean')
        toolbutton.connect('clicked', self.mat_clean)
        toolbutton.set_tooltip_text('Clean selected files without data loss')
        toolbar.add(toolbutton)

        toolbutton = gtk.ToolButton(gtk.STOCK_PRINT_WARNING)
        toolbutton.set_label('Brute Clean')
        toolbutton.set_tooltip_text('Clean selected files with possible data \
            loss')
        toolbar.add(toolbutton)

        toolbutton = gtk.ToolButton(gtk.STOCK_FIND)
        toolbutton.set_label('Check')
        toolbutton.connect('clicked', self.mat_check)
        toolbutton.set_tooltip_text('Check selected files for harmful meta')
        toolbar.add(toolbutton)

        toolbutton = gtk.ToolButton(stock_id=gtk.STOCK_QUIT)
        toolbutton.connect('clicked', gtk.main_quit)
        toolbar.add(toolbutton)

        vbox = gtk.VBox(spacing=3)
        vbox.pack_start(toolbar, False, False, 0)
        return vbox

    def add_columns(self, treeview):
        '''
            Create the columns
        '''
        colname = ['Filename', 'Mimetype', 'Cleaned']

        for i, j in enumerate(colname):
            filename_column = gtk.CellRendererText()
            column = gtk.TreeViewColumn(j, filename_column, text=i + 1)
            column.set_sort_column_id(i + 1)
            treeview.append_column(column)

    def create_menu_item(self, name, func, menu, pix):
        '''
            Create a MenuItem() like Preferences, Quit, Add, Clean, ...
        '''
        item = gtk.ImageMenuItem()
        picture = gtk.Image()
        picture.set_from_stock(pix, gtk.ICON_SIZE_MENU)
        item.set_image(picture)
        item.set_label(name)
        item.connect('activate', func)
        menu.append(item)

    def create_sub_menu(self, name, menubar):
        '''
            Create a submenu like File, Edit, Clean, ...
        '''
        submenu = gtk.Menu()
        menuitem = gtk.MenuItem()
        menuitem.set_submenu(submenu)
        menuitem.set_label(name)
        menubar.append(menuitem)
        return submenu

    def create_menu(self):
        '''
            Return a MenuBar
        '''
        menubar = gtk.MenuBar()

        file_menu = self.create_sub_menu('Files', menubar)
        self.create_menu_item('Add files', self.add_files, file_menu,
            gtk.STOCK_ADD)
        self.create_menu_item('Quit', gtk.main_quit, file_menu,
            gtk.STOCK_QUIT)

        edit_menu = self.create_sub_menu('Edit', menubar)
        self.create_menu_item('Clear the filelist', self.clear_model,
            edit_menu, gtk.STOCK_REMOVE)
        self.create_menu_item('Preferences', self.preferences, edit_menu,
            gtk.STOCK_PREFERENCES)

        clean_menu = self.create_sub_menu('Clean', menubar)
        self.create_menu_item('Clean', self.mat_clean, clean_menu,
            gtk.STOCK_PRINT_REPORT)
        self.create_menu_item('Clean (lossy way)', self.mat_clean_dirty,
            clean_menu, gtk.STOCK_PRINT_WARNING)
        self.create_menu_item('Check', self.mat_check, clean_menu,
            gtk.STOCK_FIND)

        help_menu = self.create_sub_menu('Help', menubar)
        self.create_menu_item('About', self.about, help_menu, gtk.STOCK_ABOUT)
        self.create_menu_item('Supported formats', self.supported, help_menu,
            gtk.STOCK_INFO)

        return menubar

    def add_files(self, _):
        '''
            Add the files chosed by the filechoser ("Add" button)
        '''
        chooser = gtk.FileChooserDialog(
            title='Choose files',
            parent=None,
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(gtk.STOCK_OK, 0, gtk.STOCK_CANCEL, 1))
        chooser.set_default_response(0)
        chooser.set_select_multiple(True)

        filter = gtk.FileFilter()
        filter.set_name('All files')
        filter.add_pattern('*')
        chooser.add_filter(filter)

        filter = gtk.FileFilter()
        [filter.add_mime_type(i) for i in mat.STRIPPERS.keys()]
        filter.set_name('Supported files')
        chooser.add_filter(filter)

        response = chooser.run()

        if response is 0:  # gtk.STOCK_OK
            filenames = chooser.get_filenames()
            chooser.destroy()
            for item in filenames:
                if os.path.isdir(item):  # directory
                    for root, dirs, files in os.walk(item):
                        for name in files:
                            self.populate(os.path.join(root, name))
                else:  # regular file
                    self.populate(item)
        chooser.destroy()

    def populate(self, item):
        '''
            Append selected files by add_file to the self.liststore
        '''
        cf = CFile(item, self.backup, self.add2archive)
        if cf.file is not None:
            self.liststore.append([cf, cf.file.filename,
                cf.file.mime, 'unknow'])

    def about(self, _):
        '''
            About popup
        '''
        w = gtk.AboutDialog()
        w.set_version(__version__)
        w.set_copyright('GNU Public License v2')
        w.set_comments('This software was coded during the GSoC 2011')
        w.set_website('https://gitweb.torproject.org/user/jvoisin/mat.git')
        w.set_website_label('Website')
        w.set_authors(['Julien (jvoisin) Voisin',])
        w.set_program_name('Metadata Anonymistion Toolkit')
        click = w.run()
        if click:
            w.destroy()

    def supported(self, _):
        '''
            List the supported formats
        '''
        dialog = gtk.Dialog('Supported formats', None, 0, (gtk.STOCK_CLOSE, 0))
        content_area = dialog.get_content_area()
        vbox = gtk.VBox(spacing=5)
        content_area.pack_start(vbox, True, True, 0)

        label = gtk.Label()
        label.set_markup('<big><u>Supported fileformats</u></big>')
        vbox.pack_start(label, True, True, 0)

        #parsing xml
        handler = mat.XMLParser()
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        with open('FORMATS', 'r') as f:
            parser.parse(f)

        for item in handler.list:  # list of dict : one pict per format
            #create one expander per format
            title = '%s (%s)' % (item['name'], item['extension'])
            support = '\t<b>support</b> : ' + item['support']
            metadata = '\n\t<b>metadata</b> : ' + item['metadata']
            method =  '\n\t<b>method</b> : ' + item['method']
            content = support + metadata + method

            if item['support'] == 'partial':
                content += '\n\t<b>remaining</b> : ' + item['remaining']

            expander = gtk.Expander(title)
            vbox.pack_start(expander, False, False, 0)
            label = gtk.Label()
            label.set_markup(content)
            expander.add(label)

        dialog.show_all()
        click = dialog.run()
        if click is 0:
            dialog.destroy()

    def preferences(self, _):
        '''
            Preferences popup
        '''
        dialog = gtk.Dialog('Preferences', self.window, 0, (gtk.STOCK_OK, 0))
        content_area = dialog.get_content_area()
        hbox = gtk.HBox()
        content_area.pack_start(hbox, False, False, 0)
        icon = gtk.Image()
        icon.set_from_stock(gtk.STOCK_PREFERENCES, gtk.ICON_SIZE_DIALOG)

        hbox.pack_start(icon, False, False, 0)

        table = gtk.Table(3, 2, False)  # nb rows, nb lines
        table.set_row_spacings(4)
        table.set_col_spacings(4)
        hbox.pack_start(table, True, True, 0)

        force = gtk.CheckButton('Force Clean', False)
        force.connect('toggled', self.invert, 'force')
        force.set_tooltip_text('Do not check if already clean before cleaning')
        force.set_active(self.force)

        backup = gtk.CheckButton('Backup', False)
        backup.connect('toggled', self.invert, 'backup')
        backup.set_tooltip_text('Keep a backup copy')
        backup.set_active(self.backup)

        add2archive = gtk.CheckButton('Add unsupported file to archives',
            False)
        add2archive.connect('toggled', self.invert, 'add2archive')
        add2archive.set_tooltip_text('Add non-supported (and so \
non-anonymised) file to outputed archive')
        add2archive.set_active(self.add2archive)

        table.attach_defaults(force, 0, 1, 0, 1)
        table.attach_defaults(backup, 0, 1, 1, 2)
        table.attach_defaults(add2archive, 0, 1, 2, 3)

        hbox.show_all()
        response = dialog.run()
        if response is 0:  # gtk.STOCK_OK
            dialog.destroy()

    def invert(self, _, name):  # still not better :/
        '''
            Invert a preference state
        '''
        if name is 'force':
            self.force = not self.force
        elif name is 'add2archive':
            self.add2archive = not self.add2archive
        elif name is 'backup':
            self.backup = not self.backup

    def clear_model(self, _):
        '''
            Clear the whole list of files
        '''
        self.liststore.clear()

    def all_if_empy(self, iterator):
        '''
            if no elements are selected, all elements are processed
            thank's to this function
        '''
        if not iterator:
            return xrange(len(self.liststore))
        else:
            return iterator

    def mat_check(self, _):
        '''
            Check if selected elements are clean
        '''
        _, iterator = self.selection.get_selected_rows()
        iterator = self.all_if_empy(iterator)
        for i in iterator:
            if self.liststore[i][0].file.is_clean():
                string = 'clean'
            else:
                string = 'dirty'
            logging.info('%s is %s' % (self.liststore[i][1], string))
            self.liststore[i][3] = string

    def mat_clean(self, _):
        '''
            Clean selected elements
        '''
        _, iterator = self.selection.get_selected_rows()
        iterator = self.all_if_empy(iterator)
        for i in iterator:
            logging.info('Cleaning %s' % self.liststore[i][1])
            if self.liststore[i][3] is not 'clean':
                if self.force:
                    self.liststore[i][0].file.remove_all()
                else:
                    if not self.liststore[i][0].file.is_clean():
                        self.liststore[i][0].file.remove_all()
            self.liststore[i][3] = 'clean'

    def mat_clean_dirty(self, _):
        '''
            Clean selected elements (ugly way)
        '''
        _, iterator = self.selection.get_selected_rows()
        iterator = self.all_if_empy(iterator)
        for i in iterator:
            logging.info('Cleaning (lossy way) %s' % self.liststore[i][1])
            if self.liststore[i][3] is not 'clean':
                if self.force:
                    self.liststore[i][0].file.remove_all_ugly()
                else:
                    if not self.liststore[i][0].file.is_clean():
                        self.liststore[i][0].file.remove_all_ugly()
            self.liststore[i][3] = 'clean'


if __name__ == '__main__':
    ListStoreApp()
    gtk.main()
