#!/usr/bin/python2.7

from gi.repository import Gtk, GObject
import os
import cli
import glob
from lib import mat

__version__ = '0.1'
__author__ = 'jvoisin'

SUPPORTED = (('image/png', 'image/jpeg', 'image/gif',
            'misc/pdf'),
            ('*.jpg', '*.jpeg', '*.png', '*.bmp', '*.pdf',
            '*.tar', '*.tar.bz2', '*.tar.gz', '*.mp3'))

class ListStoreApp:
    '''
        Main GUI class
    '''
    (COLUMN_NAME,
     COLUMN_FILEFORMAT,
     COLUMN_CLEANED,
     NUM_COLUMNS) = range(4)

    def __init__(self):
        self.files = []
        self.backup = True

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

        self.model = Gtk.ListStore(str, str, str) #name - type - cleaned

        treeview = Gtk.TreeView(model=self.model)
        treeview.set_rules_hint(True)
        self.selection = treeview.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.MULTIPLE)

        content.add(treeview)
        self.add_columns(treeview)

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
        toolbar.add(toolbutton)

        toolbutton = Gtk.ToolButton(label = 'Clean',
            stock_id=Gtk.STOCK_PRINT_REPORT)
        toolbutton.connect('clicked', self.mat_clean)
        toolbar.add(toolbutton)

        toolbutton = Gtk.ToolButton(label='Brute Clean',
            stock_id=Gtk.STOCK_PRINT_WARNING)
        toolbar.add(toolbutton)

        toolbutton = Gtk.ToolButton(label='Check', stock_id=Gtk.STOCK_FIND)
        toolbutton.connect('clicked', self.mat_check)
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
        model = treeview.get_model()

        # column for filename
        filenameColumn = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Filename", filenameColumn,
                                    text=self.COLUMN_NAME)
        column.set_sort_column_id(self.COLUMN_NAME)
        treeview.append_column(column)

        # column for fileformat
        fileformatColumn = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Fileformat", fileformatColumn,
                                    text=self.COLUMN_FILEFORMAT)
        column.set_sort_column_id(self.COLUMN_FILEFORMAT)
        treeview.append_column(column)

        # column for cleaned
        cleanedColumn = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Cleaned", cleanedColumn,
                                    text=self.COLUMN_CLEANED)
        column.set_sort_column_id(self.COLUMN_CLEANED)
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
        menu = Gtk.Menu()
        menum = Gtk.MenuItem()
        menum.set_submenu(menu)
        menum.set_label(name)
        menubar.append(menum)
        return menu

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
            for item in filenames: #directory
                if os.path.isdir(item):
                    for root, dirs, files in os.walk(item):
                        for name in files:
                            self.populate(os.path.join(root, name))
                else: #regular file
                    self.populate(item)
        chooser.destroy()

    def populate(self, item):
        try:
            cfile = mat.create_class_file(item, self.backup)
        except:
            cfile = None

        if cfile is not None:
            self.files.append(cfile)
            self.model.append([cfile.filename, cfile.mime, 'unknow'])

    def about(self, button=None):
        w = Gtk.AboutDialog()
        w.set_version(__version__)
        w.set_copyright('GNU GPLv2')
        w.set_comments('This software was coded during the GSoC 2011')
        w.set_website('https://gitweb.torproject.org/user/jvoisin/mat.git')
        w.set_website_label('Website')
        w.set_authors(['Julien (jvoisin) Voisin',])
        w.set_program_name('Metadata Anonymistion Toolkit')
        click = w.run()
        if click:
            w.destroy()

    def preferences(self, button=None):
        pass

    def clear_model(self, button=None):
        self.model.clear()

    def mat_check(self, button=None):#OMFG, I'm so ugly !
        self.clear_model()
        for item in self.files:
            if item.is_clean():
                string = 'clean'
            else:
                string = 'dirty'
            self.model.append([item.filename, item.mime, string])

    def mat_clean(self, button=None):#I am dirty too
        self.clear_model
        for item in self.files:
            item.remove_all()
            self.model.append([item.shortname, item.mime, 'clean'])

    def mat_clean_dirty(self, button=None):#And me too !
        self.clear_model()
        for item in self.files:
            item.remove_all_ugly()
            self.model.append([item.shortname, item.mime, 'clean'])

def main():
    app = ListStoreApp()
    Gtk.main()

if __name__ == '__main__':
    main()
