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
        self.window.connect('destroy', self.close)

        self.edit_widgets = {
                'name': self.widgets.get_widget('name'),
                'title': self.widgets.get_widget('title'),
                'source': self.widgets.get_widget('source')
        }


        self.treeview = self.widgets.get_widget('site_map')
        self.selection = self.treeview.get_selection()
        self.selection.set_mode(gtk.SELECTION_SINGLE)
        self.selection.connect("changed", self.selection_changed)
        self.populate_tree()

        self.modules_vbox = self.widgets.get_widget('modules')
        self.populate_modules()

        self.templates_combo = self.widgets.get_widget('template')
        self.populate_templates()

        self.custom_area = gtk.HBox()
        self.widgets.get_widget('right_pane').pack_start(self.custom_area)
        self.source_editor = self.widgets.get_widget('editor')

        self.window.show_all()

        self.widgets.signal_autoconnect({
                        'generate': self.generate,
                        'new_node': self.new_node,
                        'new_child': self.new_child,
                        'remove_node': self.remove_node,
                        'move_up': self.move_up,
                        'move_down': self.move_down,
                        'show_editor': self.show_editor})
        self.widgets.get_widget('name').connect('changed', self.text_edited, 0)
        self.widgets.get_widget('title').connect('changed', self.text_edited, 1)
        self.widgets.get_widget('source').connect('changed', self.text_edited, 4)
        self.widgets.get_widget('template').connect('changed', self.select_template)

    def generate(self, data=None):
        self.save_map()

    def populate_templates(self):
        templates = [ i for i in os.listdir('templates') if i.endswith('.tmp') ]

        self.templates_model = gtk.ListStore(gobject.TYPE_STRING)

        for template in templates:
            self.templates_model.append([template])

        cell = gtk.CellRendererText()
        self.templates_combo.set_model(self.templates_model)
        self.templates_combo.pack_start(cell)
        self.templates_combo.add_attribute(cell, 'text', 0)

    def populate_modules(self):
        modules = [ i[:-3] for i in os.listdir('modules') if i.endswith('.py') and i != '__init__.py' ]

        self.checks = {}
        self.modules_vbox.foreach(self.modules_vbox.remove)

        for module in modules:
            checkbox = gtk.CheckButton(module)
            self.checks[checkbox] = module
            self.modules_vbox.pack_start(checkbox, False)
            checkbox.connect("toggled", self.module_checked)

    def module_checked(self, check):
        model, iter = self.selection.get_selected()
        if not iter:
            return

        modules = self.model.get(iter, 3)[0]
        module = self.checks[check]
        if check.get_active():
            if not module in modules:
                modules.append(module)
        else:
            if module in modules:
                modules.remove(module)

        self.model.set(iter, 3, modules)

    def text_edited(self, entry, column=None):
        if column == None:
            return

        model, iter = self.selection.get_selected()
        if not iter:
            return

        self.model.set(iter, column, entry.get_text())

    def select_template(self, combo):
        model, iter = self.selection.get_selected()
        if not iter:
            return
        
        template_iter = combo.get_active_iter()
        template = self.templates_model.get(template_iter, 0)[0]

        self.model.set(iter, 2, template)

    def move_up(self, btn):
        model, iter = self.selection.get_selected()
        if not iter:
            return

        if self.model.iter_parent(iter):
            parent = self.model.iter_parent(iter)
            iter_first = self.model.iter_nth_child(parent, 0)
        else:
            iter_first = self.model.get_iter_first()

        if self.model.get(iter, 0) == self.model.get(iter_first, 0):
            return

        while iter_first:
            if self.model.get(self.model.iter_next(iter_first), 0) == self.model.get(iter, 0):
                self.model.swap(iter_first, iter)
                break
            iter_first = self.model.iter_next(iter_first)

    def move_down(self, btn):
        model, iter = self.selection.get_selected()
        if not iter or not self.model.iter_next(iter):
            return

        self.model.swap(iter, self.model.iter_next(iter))

    def new_node(self, btn):
        model, iter = self.selection.get_selected()

        self.model.insert_after(None, iter, ['New', u'', '', [], ''])

    def new_child(self, btn):
        model, iter = self.selection.get_selected()

        if self.model.iter_parent(iter):
            return

        self.model.append(iter, ['New', u'', '', [], ''])

    def remove_node(self, btn):
        model, iter = self.selection.get_selected()

        if not iter:
            return

        self.model.remove(iter)

    def selection_changed(self, selection, data=None):
        self.save_map()

        model, iter = selection.get_selected()
        if not iter:
            return

        self.edit_widgets['name'].set_text(self.model.get(iter, 0)[0])
        self.edit_widgets['title'].set_text(self.model.get(iter, 1)[0])
        self.edit_widgets['source'].set_text(self.model.get(iter, 4)[0])

        modules = self.model.get(iter, 3)[0]

        for i in self.checks.keys():
            if self.checks[i] in modules:
                i.set_active(True)
            else:
                i.set_active(False)

        template = self.model.get(iter, 2)[0]

        iter = self.templates_model.get_iter_first()
        index = None
        while iter:
            if self.templates_model.get(iter, 0)[0] == template:
                index = iter
                break
            iter = self.templates_model.iter_next(iter)

        if not index:
            index = self.templates_model.get_iter_first()
            return

        self.templates_combo.set_active_iter(index)

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

        json.dump(map, open('site_map.json', 'w'), encoding='utf-8')
#        print json.dumps(map, encoding='utf-8')
        self.map = map

    def serialize_node(self, iter):
        columns = ['name', 'title', 'template', 'modules', 'sources']
        
        node = dict(zip(columns, self.model.get(iter, *range(5))))

        child = self.model.iter_children(iter)
        if child:
            node['subs'] = []
            while child:
                node['subs'].append(self.serialize_node(child))
                child = self.model.iter_next(child)
        else:
            node['subs'] = []

        return node

    def show_editor(self, btn):
        self.custom_area.foreach(self.custom_area.remove)

        if self.source_editor.get_parent():
            self.source_editor.reparent(self.custom_area)
        else:
            self.custom_area.add(self.source_editor)

    def close(self):
        self.save_map()
        gtk.main_quit()

    def loop(self):
        try:
            gtk.main()
        except KeyboardInterrupt:
            self.save_map()

if __name__ == '__main__':
    gui = GeneratorGUI()
    gui.loop()
