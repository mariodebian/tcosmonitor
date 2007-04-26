#!/usr/bin/env python

import pango
import gtk

w = gtk.Window()
w.set_default_size(150, 100)
w.connect("destroy", gtk.main_quit)

alignment = gtk.Alignment(0.5, 0.5, 0, 0) # set xscale to 1 to expand
w.add(alignment)

table = gtk.Table(2, 1)
alignment.add(table)

label = gtk.Label("Title:")
table.attach(label, 0, 1, 0, 1, gtk.FILL, 0)

label = gtk.Label("Really long text")
label.set_ellipsize(pango.ELLIPSIZE_END)
table.attach(label, 1, 2, 0, 1, gtk.FILL, 0) # add gtk.EXPAND to expand

w.show_all()
gtk.main()
