#!/usr/bin/env python
#
# [SNIPPET_NAME: Pack Box]
# [SNIPPET_CATEGORIES: PyGTK]
# [SNIPPET_DESCRIPTION: Handling packing]
# [SNIPPET_DOCS: http://www.pygtk.org/docs/pygtk/class-gtkbox.html]

# example packbox.py

import pygtk
pygtk.require('2.0')
import gtk
import sys, string

# Helper function that makes a new hbox filled with button-labels. Arguments
# for the variables we're interested are passed in to this function.  We do
# not show the box, but do show everything inside.

def make_box(homogeneous, spacing, expand, fill, padding):

    # Create a new hbox with the appropriate homogeneous
    # and spacing settings
    box = gtk.HBox(homogeneous, spacing)

    # Create a series of buttons with the appropriate settings
    button = gtk.Button("box.pack")
    box.pack_start(button, expand, fill, padding)
    button.show()

    button = gtk.Button("(button,")
    box.pack_start(button, expand, fill, padding)
    button.show()

    # Create a button with the label depending on the value of
    # expand.
    if expand == True:
        button = gtk.Button("True,")
    else:
        button = gtk.Button("False,")

    box.pack_start(button, expand, fill, padding)
    button.show()

    # This is the same as the button creation for "expand"
    # above, but uses the shorthand form.
    button = gtk.Button(("False,", "True,")[fill==True])
    box.pack_start(button, expand, fill, padding)
    button.show()

    padstr = "%d)" % padding

    button = gtk.Button(padstr)
    box.pack_start(button, expand, fill, padding)
    button.show()
    return box

class PackBox1:
    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False

    def __init__(self, which):

        # Create our window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        # You should always remember to connect the delete_event signal
        # to the main window. This is very important for proper intuitive
        # behavior
        self.window.connect("delete_event", self.delete_event)
        self.window.set_border_width(10)

        # We create a vertical box (vbox) to pack the horizontal boxes into.
        # This allows us to stack the horizontal boxes filled with buttons one
        # on top of the other in this vbox.
        box1 = gtk.VBox(False, 0)

        # which example to show. These correspond to the pictures above.
        if which == 1:
            # create a new label.
            label = gtk.Label("HBox(False, 0)")

            # Align the label to the left side.  We'll discuss this method
            # and others in the section on Widget Attributes.
            label.set_alignment(0, 0)

            # Pack the label into the vertical box (vbox box1).  Remember that
            # widgets added to a vbox will be packed one on top of the other in
            # order.
            box1.pack_start(label, False, False, 0)

            # Show the label
            label.show()

            # Call our make box function - homogeneous = False, spacing = 0,
            # expand = False, fill = False, padding = 0
            box2 = make_box(False, 0, False, False, 0)
            box1.pack_start(box2, False, False, 0)
            box2.show()

            # Call our make box function - homogeneous = False, spacing = 0,
            # expand = True, fill = False, padding = 0
            box2 = make_box(False, 0, True, False, 0)
            box1.pack_start(box2, False, False, 0)
            box2.show()

            # Args are: homogeneous, spacing, expand, fill, padding
            box2 = make_box(False, 0, True, True, 0)
            box1.pack_start(box2, False, False, 0)
            box2.show()

            # Creates a separator, we'll learn more about these later,
            # but they are quite simple.
            separator = gtk.HSeparator()

            # Pack the separator into the vbox. Remember each of these
            # widgets is being packed into a vbox, so they'll be stacked
            # vertically.
            box1.pack_start(separator, False, True, 5)
            separator.show()

            # Create another new label, and show it.
            label = gtk.Label("HBox(True, 0)")
            label.set_alignment(0, 0)
            box1.pack_start(label, False, False, 0)
            label.show()

            # Args are: homogeneous, spacing, expand, fill, padding
            box2 = make_box(True, 0, True, False, 0)
            box1.pack_start(box2, False, False, 0)
            box2.show()

            # Args are: homogeneous, spacing, expand, fill, padding
            box2 = make_box(True, 0, True, True, 0)
            box1.pack_start(box2, False, False, 0)
            box2.show()

            # Another new separator.
            separator = gtk.HSeparator()
            # The last 3 arguments to pack_start are:
            # expand, fill, padding.
            box1.pack_start(separator, False, True, 5)
            separator.show()
        elif which == 2:
            # Create a new label, remember box1 is a vbox as created
            # near the beginning of __init__()
            label = gtk.Label("HBox(False, 10)")
            label.set_alignment( 0, 0)
            box1.pack_start(label, False, False, 0)
            label.show()

            # Args are: homogeneous, spacing, expand, fill, padding
            box2 = make_box(False, 10, True, False, 0)
            box1.pack_start(box2, False, False, 0)
            box2.show()

            # Args are: homogeneous, spacing, expand, fill, padding
            box2 = make_box(False, 10, True, True, 0)
            box1.pack_start(box2, False, False, 0)
            box2.show()

            separator = gtk.HSeparator()
            # The last 3 arguments to pack_start are:
            # expand, fill, padding.
            box1.pack_start(separator, False, True, 5)
            separator.show()

            label = gtk.Label("HBox(False, 0)")
            label.set_alignment(0, 0)
            box1.pack_start(label, False, False, 0)
            label.show()

            # Args are: homogeneous, spacing, expand, fill, padding
            box2 = make_box(False, 0, True, False, 10)
            box1.pack_start(box2, False, False, 0)
            box2.show()

            # Args are: homogeneous, spacing, expand, fill, padding
            box2 = make_box(False, 0, True, True, 10)
            box1.pack_start(box2, False, False, 0)
            box2.show()

            separator = gtk.HSeparator()
            # The last 3 arguments to pack_start are:
            # expand, fill, padding.
            box1.pack_start(separator, False, True, 5)
            separator.show()

        elif which == 3:

            # This demonstrates the ability to use pack_end() to
            # right justify widgets. First, we create a new box as before.
            box2 = make_box(False, 0, False, False, 0)

            # Create the label that will be put at the end.
            label = gtk.Label("end")
            # Pack it using pack_end(), so it is put on the right
            # side of the hbox created in the make_box() call.
            box2.pack_end(label, False, False, 0)
            # Show the label.
            label.show()

            # Pack box2 into box1
            box1.pack_start(box2, False, False, 0)
            box2.show()

            # A separator for the bottom.
            separator = gtk.HSeparator()

            # This explicitly sets the separator to 400 pixels wide by 5
            # pixels high. This is so the hbox we created will also be 400
            # pixels wide, and the "end" label will be separated from the
            # other labels in the hbox. Otherwise, all the widgets in the
            # hbox would be packed as close together as possible.
            separator.set_size_request(400, 5)
            # pack the separator into the vbox (box1) created near the start
            # of __init__()
            box1.pack_start(separator, False, True, 5)
            separator.show()

        # Create another new hbox.. remember we can use as many as we need!
        quitbox = gtk.HBox(False, 0)

        # Our quit button.
        button = gtk.Button("Quit")

        # Setup the signal to terminate the program when the button is clicked
        button.connect("clicked", lambda w: gtk.main_quit())
        # Pack the button into the quitbox.
        # The last 3 arguments to pack_start are:
        # expand, fill, padding.
        quitbox.pack_start(button, True, False, 0)
        # pack the quitbox into the vbox (box1)
        box1.pack_start(quitbox, False, False, 0)

        # Pack the vbox (box1) which now contains all our widgets, into the
        # main window.
        self.window.add(box1)

        # And show everything left
        button.show()
        quitbox.show()

        box1.show()
        # Showing the window last so everything pops up at once.
        self.window.show()

def main():
    # And of course, our main loop.
    gtk.main()
    # Control returns here when main_quit() is called
    return 0

if __name__ =="__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("usage: packbox.py num, where num is 1, 2, or 3.\n")
        sys.exit(1)
    PackBox1(string.atoi(sys.argv[1]))
    main()
