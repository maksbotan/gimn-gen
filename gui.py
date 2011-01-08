#!/usr/bin/env python

import os, json
import gobject, gtk, gtk.glade

class GeneratorGUI():
    """
    Main class for GUI
    """

    def __init__(self):
        self.load_map()

        self.widgets = gtk.glade.XML('gui.ui')

        self.window = self.widgets.get_widget('main_window')
        self.window.connect('destroy', gtk.main_quit)

        self.treeview = self.widgets.get_widget('site_map')
        self.selection = self.treeview.get_selection()
        self.selection.set_mode(gtk.SELECTION_SINGLE)
        self.selection.connect("changed", self.selection_changed)
        self.populate_tree()

        self.modules_vbox = self.widgets.get_widget('modules')
        self.populate_modules()

        self.window.show_all()
        self.widgets.signal_autoconnect({'generate': self.generate})

    def generate(self, data=None):
        self.save_map()

    def populate_modules(self):
        modules = [ i for i in os.listdir('modules') if i.endswith('.py') and i != '__init__.py' ]

        self.checks = {}
        self.modules_vbox.foreach(self.modules_vbox.remove)

        for module in modules:
            checkbox = gtk.CheckButton(module)
            self.checks[checkbox] = module
            self.modules_vbox.pack_start(checkbox)
            
    def selection_changed(self, selection, data=None):
        pass

    def populate_tree(self):
        self.model = gtk.TreeStore(
                        gobject.TYPE_STRING,    #name
                        gobject.TYPE_STRING,    #title
                        gobject.TYPE_STRING,    #template
                        gobject.TYPE_PYOBJECT,  #modules
                        gobject.TYPE_STRING     #sources
                     )

        self.treeview.set_model(self.model)

        self.treeview.append_column(
                gtk.TreeViewColumn(None, gtk.CellRendererText(), text=1))

        for node in self.map:
            self.add_node_to_tree(node, None)

    def add_node_to_tree(self, node, parent):
        iter = self.model.append(parent, [
                                            node['name'],
                                            node['title'],
                                            node['template'],
                                            node['modules'],
                                            node['sources']
                                         ])
        for sub in node['subs']:
            self.add_node_to_tree(sub, iter)

    def load_map(self):
        self.map = json.load(open('site_map.json', 'r'), encoding='utf-8')

    def save_map(self):
        iter = self.model.get_iter_first()
        if not iter:
            return
        
        map = []
        while iter:
            map.append(self.serialize_node(iter))
            iter = self.model.iter_next(iter)

#        json.dump(open('site_map.json', 'r'), self.map, encoding='utf-8')
        print json.dumps(map, encoding='utf-8')
        self.map = map

    def serialize_node(self, iter):
        columns = ['name', 'title', 'template', 'modules', 'sources']
        
        node = dict(zip(columns, self.model.get(iter, *range(5))))

        child = self.model.iter_children(iter)
        if child:
            node['subs'] = self.serialize_node(child)
        else:
            node['subs'] = []

        return node

    def loop(self):
        gtk.main()

if __name__ == '__main__':
    gui = GeneratorGUI()
    gui.loop()
