#!/usr/bin/env python

from gi.repository import Gtk, GObject, Gdk
import os
import glob
import logging
from lib import mat

__version__ = '0.1'
__author__ = 'jvoisin'

logging.basicConfig(level = mat.LOGGING_LEVEL)

SUPPORTED = (('image/png', 'image/jpeg', 'image/gif',
            'misc/pdf'),
            ('*.jpg', '*.jpeg', '*.png', '*.bmp', '*.pdf',
            '*.tar', '*.tar.bz2', '*.tar.gz', '*.mp3'))

class cfile(GObject.GObject):
    '''
        Contain the class-file of the file "path"
        This class exist just to be "around" my parser.Generic_parser class,
        since Gtk.ListStore does not accept it.
    '''
    def __init__(self, path, backup, add2archive):
        GObject.GObject.__init__(self)
        try:
            self.file = mat.create_class_file(path, backup, add2archive)
        except:
            self.file = None

class ListStoreApp:
    '''
        Main GUI class
    '''
    def __init__(self):
        #preferences
        self.backup = True
        self.force = False
        self.add2archive = True

        self.window = Gtk.Window()
        self.window.set_title('Metadata Anonymisation Toolkit %s' % __version__)
        self.window.connect('destroy', Gtk.main_quit)
        self.window.set_default_size(800, 600)

        vbox = Gtk.VBox()
        self.window.add(vbox)

        menubar = self.create_menu()
        toolbar = self.create_toolbar()
        content = Gtk.ScrolledWindow()
        vbox.pack_start(menubar, False, True, 0)
        vbox.pack_start(toolbar, False, True, 0)
        vbox.pack_start(content, True, True, 0)

        #parser.class - name - type - cleaned
        self.liststore= Gtk.ListStore(cfile ,str, str, str)

        treeview = Gtk.TreeView(model=self.liststore)
        treeview.set_search_column(1) #name column is searchable
        treeview.set_rules_hint(True) #alternate colors for rows
        treeview.set_rubber_banding(True) #mouse selection
        treeview.drag_dest_set(Gtk.DestDefaults.ALL, None, Gdk.DragAction.COPY)
        self.add_columns(treeview)
        self.selection = treeview.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.MULTIPLE)

        content.add(treeview)

        self.statusbar = Gtk.Statusbar()
        self.statusbar.push(1, 'Ready')
        vbox.pack_start(self.statusbar, False, False, 0)

        self.window.show_all()

    def create_toolbar(self):
        '''
            Returns a vbox object, which contains a toolbar with buttons
        '''
        toolbar = Gtk.Toolbar()

        toolbutton = Gtk.ToolButton(label = 'Add', stock_id=Gtk.STOCK_ADD)
        toolbutton.connect('clicked', self.add_files)
        toolbutton.set_tooltip_text('Add files')
        toolbar.add(toolbutton)

        toolbutton = Gtk.ToolButton(label = 'Clean',
            stock_id=Gtk.STOCK_PRINT_REPORT)
        toolbutton.connect('clicked', self.mat_clean)
        toolbutton.set_tooltip_text('Clean selected files without data loss')
        toolbar.add(toolbutton)

        toolbutton = Gtk.ToolButton(label='Brute Clean',
            stock_id=Gtk.STOCK_PRINT_WARNING)
        toolbutton.set_tooltip_text('Clean selected files with possible data loss')
        toolbar.add(toolbutton)

        toolbutton = Gtk.ToolButton(label='Check', stock_id=Gtk.STOCK_FIND)
        toolbutton.connect('clicked', self.mat_check)
        toolbutton.set_tooltip_text('Check selected files for harmful meta')
        toolbar.add(toolbutton)

        toolbutton = Gtk.ToolButton(stock_id=Gtk.STOCK_QUIT)
        toolbutton.connect('clicked', Gtk.main_quit)
        toolbar.add(toolbutton)

        vbox = Gtk.VBox(spacing=3)
        vbox.pack_start(toolbar, False, False, 0)
        return vbox

    def add_columns(self, treeview):
        '''
            Create the columns
        '''
        colname = ['Filename', 'Mimetype', 'Cleaned']

        for i, j in enumerate(colname):
            filenameColumn = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(j, filenameColumn, text=i+1)
            column.set_sort_column_id(i+1)
            treeview.append_column(column)

    def create_menu_item(self, name, func, menu, pix):
        '''
            Create a MenuItem() like Preferences, Quit, Add, Clean, ...
        '''
        item = Gtk.ImageMenuItem()
        picture = Gtk.Image.new_from_stock(pix, Gtk.IconSize.MENU)
        item.set_image(picture)
        item.set_label(name)
        item.connect('activate', func)
        menu.append(item)

    def create_sub_menu(self, name, menubar):
        '''
            Create a submenu like File, Edit, Clean, ...
        '''
        submenu = Gtk.Menu()
        menuitem = Gtk.MenuItem()
        menuitem.set_submenu(submenu)
        menuitem.set_label(name)
        menubar.append(menuitem)
        return submenu

    def create_menu(self):
        '''
            Return a MenuBar
        '''
        menubar = Gtk.MenuBar()

        file_menu = self.create_sub_menu('Files', menubar)
        self.create_menu_item('Add files', self.add_files, file_menu,
            Gtk.STOCK_ADD)
        self.create_menu_item('Quit', Gtk.main_quit, file_menu,
            Gtk.STOCK_QUIT)

        edit_menu = self.create_sub_menu('Edit', menubar)
        self.create_menu_item('Clear the filelist', self.clear_model, edit_menu,
            Gtk.STOCK_REMOVE)
        self.create_menu_item('Preferences', self.preferences, edit_menu,
            Gtk.STOCK_PREFERENCES)

        clean_menu = self.create_sub_menu('Clean', menubar)
        self.create_menu_item('Clean', self.mat_clean, clean_menu,
            Gtk.STOCK_PRINT_REPORT)
        self.create_menu_item('Clean (lossy way)', self.mat_clean_dirty,
            clean_menu, Gtk.STOCK_PRINT_WARNING)
        self.create_menu_item('Check', self.mat_check, clean_menu,
            Gtk.STOCK_FIND)

        help_menu = self.create_sub_menu('Help', menubar)
        self.create_menu_item('About', self.about, help_menu, Gtk.STOCK_ABOUT)

        return menubar

    def create_filter(self):
        '''
            Return a filter for
            supported content
        '''
        filter = Gtk.FileFilter()
        filter.set_name('Supported files')
        for item in SUPPORTED[0]: #add by mime
            filter.add_mime_type(item)
        for item in SUPPORTED[1]: #add by extension
            filter.add_pattern(item)
        return filter

    def add_files(self, button):
        '''
            Add the files chosed by the filechoser ("Add" button)
        '''
        chooser = Gtk.FileChooserDialog(
            title='Choose files',
            parent=None,
            action=Gtk.FileChooserAction.OPEN,
            buttons=(Gtk.STOCK_OK, 0, Gtk.STOCK_CANCEL, 1)
            )
        chooser.set_default_response(0)
        chooser.set_select_multiple(True)

        filter = Gtk.FileFilter()
        filter.set_name('All files')
        filter.add_pattern('*')
        chooser.add_filter(filter)
        chooser.add_filter(self.create_filter())

        response = chooser.run()

        if response is 0: #Gtk.STOCK_OK
            filenames = chooser.get_filenames()
            chooser.destroy()
            for item in filenames:
                if os.path.isdir(item): #directory
                    for root, dirs, files in os.walk(item):
                        for name in files:
                            self.populate(os.path.join(root, name))
                else: #regular file
                    self.populate(item)
        chooser.destroy()

    def populate(self, item):
        '''
            Append selected files by add_file to the self.liststore
        '''
        cf = cfile(item, self.backup, self.add2archive)
        if cf.file is not None:
            self.liststore.append([cf, cf.file.filename, cf.file.mime,'unknow'])

    def about(self, button=None):
        w = Gtk.AboutDialog()
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

    def preferences(self, button=None):
        '''
            Preferences popup
        '''
        dialog = Gtk.Dialog('Preferences', self.window, 0, (Gtk.STOCK_OK, 0))
        content_area = dialog.get_content_area()
        hbox = Gtk.HBox()
        content_area.pack_start(hbox, False, False, 0)
        icon = Gtk.Image(stock=Gtk.STOCK_PREFERENCES,
            icon_size=Gtk.IconSize.DIALOG)#the little picture on the left

        hbox.pack_start(icon, False, False, 0)

        table = Gtk.Table(3, 2, False)#nb rows, nb lines
        table.set_row_spacings(4)
        table.set_col_spacings(4)
        hbox.pack_start(table, True, True, 0)

        force = Gtk.CheckButton('Force Clean', False)
        force.connect('toggled', self.invert, 'force')
        force.set_tooltip_text('Do not check if already clean before cleaning.')
        force.set_active(self.force)

        backup = Gtk.CheckButton('Backup', False)
        backup.connect('toggled', self.invert, 'backup')
        backup.set_tooltip_text('Keep a backup copy.')
        backup.set_active(self.backup)

        add2archive = Gtk.CheckButton('Add unsupported file to archives', False)
        add2archive.connect('toggled', self.invert, 'add2archive')
        add2archive.set_tooltip_text('Add non-supported (and so non-anonymised)\
 file to outputed archive.')
        add2archive.set_active(self.add2archive)

        table.attach_defaults(force, 0, 1, 0, 1)
        table.attach_defaults(backup, 0, 1, 1, 2)
        table.attach_defaults(add2archive, 0, 1, 2, 3)

        hbox.show_all()
        response = dialog.run()
        if response is 0:#Gtk.STOCK_OK
            dialog.destroy()

    def invert(self, button, name): #Still not better :/
        if name is 'force':
            self.force = not self.force
        elif name is 'ugly':
            self.ugly = not self.ugly
        elif name is 'backup':
            self.backup = not self.backup

    def clear_model(self, button=None):
        self.liststore.clear()

    def all_if_empy(self, iter):
        if not iter:
            return xrange(len(self.liststore))
        else:
            return iter

    def mat_check(self, button=None):
        _, iter = self.selection.get_selected_rows()
        iter = self.all_if_empy(iter)
        for i in iter:
            if self.liststore[i][0].file.is_clean():
                string = 'clean'
            else:
                string = 'dirty'
            logging.info('%s is %s' % (self.liststore[i][1], string))
            self.liststore[i][3] = string

    def mat_clean(self, button=None):
        _, iter = self.selection.get_selected_rows()
        iter = self.all_if_empy(iter)
        for i in iter:
            logging.info('Cleaning %s' % self.liststore[i][1])
            if self.liststore[i][3] is not 'clean':
                if self.force:
                    self.liststore[i][0].file.remove_all()
                else:
                    if not self.liststore[i][0].file.is_clean():
                        self.liststore[i][0].file.remove_all()
            self.liststore[i][3] = 'clean'

    def mat_clean_dirty(self, button=None):
        _, iter = self.selection.get_selected_rows()
        iter = self.all_if_empy(iter)
        for i in iter:
            logging.info('Cleaning (lossy way) %s' % self.liststore[i][1])
            if self.liststore[i][3] is not 'clean':
                if self.force:
                    self.liststore[i][0].file.remove_all_ugly()
                else:
                    if not self.liststore[i][0].file.is_clean():
                        self.liststore[i][0].file.remove_all_ugly()
            self.liststore[i][3] = 'clean'

def main():
    app = ListStoreApp()
    Gtk.main()

if __name__ == '__main__':
    main()
