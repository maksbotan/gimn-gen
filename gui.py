#!/usr/bin/env python

import os, json
import gobject, gtk, gtk.glade

#Import other gui parts
import source_editor, site_control, modules_editor

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

        self.custom_area = gtk.Notebook()
        self.widgets.get_widget('right_pane').pack_start(self.custom_area)
        self.source_editor = source_editor.SourceEditor()
        self.custom_area.append_page(self.source_editor.get_content(), gtk.Label("Source editor"))

        self.site_control = site_control.SiteControl(self.widgets)
        self.custom_area.append_page(self.site_control.get_content(), gtk.Label("Site control"))

        self.modules_editor = modules_editor.ModulesEditor(self.widgets, self.populate_modules)
        self.custom_area.append_page(self.modules_editor.get_content(), gtk.Label("Modules editor"))

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
        modules = [ i[:-5] for i in os.listdir('modules') if i.endswith('.json') and i != '__init__.py' ]

        self.checks = {}
        self.modules_vbox.foreach(self.modules_vbox.remove)

        for module in modules:
            checkbox = gtk.CheckButton(module)
            self.checks[checkbox] = module
            self.modules_vbox.pack_start(checkbox, False)
            checkbox.connect("toggled", self.module_checked)
            checkbox.show()

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

        template = self.templates_model.get(self.templates_model.get_iter_first(), 0)[0]
        self.model.insert_after(None, iter, ['New', u'', template, [], 'fish.cont'])

    def new_child(self, btn):
        model, iter = self.selection.get_selected()

        template = self.templates_model.get(self.templates_model.get_iter_first(), 0)[0]
        self.model.append(iter, ['New', u'', template, [], 'fish.cont'])

    def remove_node(self, btn):
        model, iter = self.selection.get_selected()

        if not iter:
            return

        self.model.remove(iter)

    def selection_changed(self, selection, data=None):
        self.save_map()
        try:
            self.source_editor.flush_buffer()
        except AttributeError:
            pass

        model, iter = selection.get_selected()
        if not iter:
            return

        self.edit_widgets['name'].set_text(self.model.get(iter, 0)[0])
        self.edit_widgets['title'].set_text(self.model.get(iter, 1)[0])
        self.edit_widgets['source'].set_text(self.model.get(iter, 4)[0])

        content = self.model.get(iter, 4)[0]
        self.source_editor.allocate_buffer(content, len(self.model.get_path(iter))-1, self.make_path(iter))
        self.source_editor.switch_to_buffer(content)
        self.source_editor.load_file_to_buffer(os.path.join('content', content), content)

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

    def make_path(self, iter):
        """
        Auxillary function to calculate path to current node relative to site root

        params:
            - iter: gtk.TreeIter pointing to current node
        """

        #Get TreeModel path to node
        model_path = self.model.get_path(iter)

        #Containter for path elements
        path = []

        #Scan nodes from top to depth
        for i in xrange(len(model_path)-1):
            #Currently scanned node
            node_iter = self.model.get_iter(model_path[:i+1])
            node_name = self.model.get(node_iter, 0)[0]
            #Store its name in path
            path.append(node_name)

        return "/".join(path)

    def show_editor(self, btn):
        #TODO: Switch editor to current buffer
        pass

    def close(self, wnd):
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
