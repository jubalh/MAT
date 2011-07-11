#!/usr/bin/python2.7

from gi.repository import Gtk, GObject
#import cli

__version__ = '0.1'
__author__ = 'jvoisin'

class File:
    '''
        Represent a File
    '''
    def __init__(self, name, fileformat, cleaned):
        self.name = name
        self.fileformat = fileformat
        self.cleaned = cleaned

# initial data we use to fill in the store
data = [File('test.txt', 'PLAIN TEXT', 0),
        File('ugly.pdf', 'UGLY_PDF', 2),
        File('ugly.doc', 'UGLY_OL2', 1),
]

class ListStoreApp:
    '''
        Main GUI class
    '''
    (COLUMN_NAME,
     COLUMN_FILEFORMAT,
     COLUMN_CLEANED,
     NUM_COLUMNS) = range(4)

    def __init__(self):
        self.window = Gtk.Window()
        self.window.set_title('Metadata Anonymisation Toolkit %s' % __version__)
        self.window.connect('destroy', Gtk.main_quit)

        vbox = Gtk.VBox()
        self.window.add(vbox)
        self.window.connect('destroy', Gtk.main_quit)

        toolbar = Gtk.Toolbar()
        toolbutton = Gtk.ToolButton(label = 'Clean', stock_id=Gtk.STOCK_CLEAR)
        toolbar.add(toolbutton)
        toolbutton = Gtk.ToolButton(label='Check', stock_id=Gtk.STOCK_APPLY)
        toolbar.add(toolbutton)
        toolbutton = Gtk.ToolButton(stock_id=Gtk.STOCK_QUIT)
        toolbar.add(toolbutton)
        vbox.pack_start(toolbar, False, False, 0)

        sw = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw.set_policy(Gtk.PolicyType.NEVER,
                      Gtk.PolicyType.AUTOMATIC)
        vbox.pack_start(sw, True, True, 0)

        self.create_model()
        treeview = Gtk.TreeView(model=self.model)
        treeview.set_rules_hint(True)
        sw.add(treeview)

        self.add_columns(treeview)

        self.window.set_default_size(800, 600)
        self.window.show_all()


    def create_model(self):
        self.model = Gtk.ListStore(str, str, str,) #name - type - cleaned
        for item in data:
            if item.cleaned is 0:
                s = 'clean'
            elif item.cleaned is 1:
                s = 'dirty'
            else:
                s = 'unknow'
            self.model.append([item.name,
                                item.fileformat,
                                s
                            ])

    def add_columns(self, treeview):
        model = treeview.get_model()

        # column for filename
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Filename", renderer,
                                    text=self.COLUMN_NAME)
        column.set_sort_column_id(self.COLUMN_NAME)
        treeview.append_column(column)

        # column for fileformat
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Fileformat", renderer,
                                    text=self.COLUMN_FILEFORMAT)
        column.set_sort_column_id(self.COLUMN_FILEFORMAT)
        treeview.append_column(column)

        # column for cleaned
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Cleaned", renderer,
                                    text=self.COLUMN_CLEANED)
        column.set_sort_column_id(self.COLUMN_CLEANED)
        treeview.append_column(column)

def main(demoapp=None):
    app = ListStoreApp()
    Gtk.main()

if __name__ == '__main__':
    main()

