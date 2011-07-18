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
            Crete the columns
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

    def create_menu(self):
        menubar = Gtk.MenuBar()

        file_menu = Gtk.Menu()

        filem = Gtk.MenuItem()
        filem.set_submenu(file_menu)
        filem.set_label('Files')

        add_ = Gtk.MenuItem()
        add_.set_label('Add files')
        add_.connect('activate', self.add_files)
        file_menu.append(add_)

        quit_ = Gtk.MenuItem()
        quit_.set_label('Quit')
        quit_.connect('activate', Gtk.main_quit)
        file_menu.append(quit_)
        menubar.append(filem)

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

    def mat_check(self, button):#OMFG, I'm so ugly !
        self.model.clear()
        for item in self.files:
            if item.is_clean():
                string = 'clean'
            else:
                string = 'dirty'
            self.model.append([item.filename, item.mime, string])

    def mat_clean(self, button):#I am dirty too
        self.model.clear()
        for item in self.files:
            item.remove_all()
            self.model.append([item.shortname, item.mime, 'clean'])

def main():
    app = ListStoreApp()
    Gtk.main()

if __name__ == '__main__':
    main()
