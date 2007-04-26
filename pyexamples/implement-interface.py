import gtk
import gobject


class EditableLabel(gtk.Label, gtk.Editable):

    def __init__(self, text):
        gtk.Label.__init__(self, text)

    def do_do_delete_text(self, start_pos, end_pos):
        self.props.label = "".join((self.props.label[:start_pos], self.props.label[end_pos:]))

gobject.type_register(EditableLabel)

if __name__ == '__main__':
    w = gtk.Window()
    vbox = gtk.VBox()
    w.add(vbox)
    label = EditableLabel("Foo Bar Zbr")
    vbox.add(label)
    bt = gtk.Button("delete word")
    def delete_word(bt):
        label.delete_text(4, 7)
    bt.connect("clicked", delete_word)
    vbox.add(bt)
    w.connect("destroy", lambda w: gtk.main_quit())
    w.show_all()
    gtk.main()
    
