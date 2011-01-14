
import os
import gtk, gobject

import source_editor

class ModulesEditor():
    """
    Class to represent module editing tab
    """

    def __init__(self, widgets_tree, update_modules_cb):
        """
        Constructor

        params:
            - widgets_tree: gtk.glade.XML object
            - update_modules_cb: Callback function to be called when modules are changed
        """
        
        #Get content container
        self.content = widgets_tree.get_widget('modules_editor')
        #Detach from useless gtk.Window
        widgets_tree.get_widget('modules_window').remove(self.content)

        self.callback = update_modules_cb

        #Create source editor and add it to the form
        self.editor = source_editor.SourceEditor('js')
        self.content.pack_start(self.editor.get_content())

        #Create model containing modules and set up combo box
        self.model = gtk.ListStore(gobject.TYPE_STRING)
        renderer = gtk.CellRendererText()
        combo = widgets_tree.get_widget('modules_combo')
        combo.set_model(self.model)
        combo.pack_start(renderer)
        combo.add_attribute(renderer, 'text', 0)
        
        #Populate it with existing modules
        self.find_modules()

        #Load first module to editor
        iter = self.model.get_iter_first()
        combo.set_active_iter(iter)
        self.module_selected(combo)

        #Connect all signals
        widgets_tree.signal_autoconnect({
            'module_selected': self.module_selected,
            'new_module': self.new_module,
            'remove_module': self.remove_module})
    
    def module_selected(self, combo):
        """
        Handler for switching current displaying module in editor
        """

        module_iter = combo.get_active_iter()
        module = self.model.get(module_iter, 0)[0]
        
        self.editor.switch_to_buffer(module)

    def new_module(self, btn):
        """
        Handler for adding new modules to list and file system
        """
        pass

    def remove_module(self, btn):
        """
        Handler for removing module from list and filesystem
        """
        pass

    def find_modules(self):
        """
        Get all modules from 'modules/*.json' and save them in gtk.ListStore
        """
        
        for module in [ i for i in os.listdir('modules') if i.endswith('.json') ]:
            self.model.append([module])
            
            self.editor.allocate_buffer(module)
            self.editor.load_file_to_buffer(os.path.join('modules', module), module)

    def get_content(self):
        """
        Return content widget for embedding in main window
        """

        return self.content
