
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
        self.combo = widgets_tree.get_widget('modules_combo')
        self.combo.set_model(self.model)
        self.combo.pack_start(renderer)
        self.combo.add_attribute(renderer, 'text', 0)
        
        #Populate it with existing modules
        self.find_modules()

        #Load first module to editor
        iter = self.model.get_iter_first()
        self.combo.set_active_iter(iter)
        self.module_selected(self.combo)

        #Connect all signals
        widgets_tree.signal_autoconnect({
            'module_selected': self.module_selected,
            'new_module': self.new_module,
            'remove_module': self.remove_module})
    
    def module_selected(self, combo):
        """
        Handler for switching current displaying module in editor
        """

        module_iter = self.combo.get_active_iter()
        if type(module_iter) != gtk.TreeIter or not self.model.iter_is_valid(module_iter):
            #Avoid some strange GTK problems
            return

        module = self.model.get(module_iter, 0)[0]
        
        self.editor.switch_to_buffer(module)

    def new_module(self, btn):
        """
        Handler for adding new modules to list and file system
        """

        name = self.input_dialog()
        while not name.endswith('.json') and not name == '':
            name = self.input_dialog()

        if os.path.exists(os.path.join('modules', name)):
            #Module already here, do nothing
            return

        #Append module to list and allocate buffer for it
        self.model.append([name])
        self.editor.allocate_buffer(name)
        #Create file for module
        open(os.path.join('modules', name), 'w')
        self.editor.load_file_to_buffer(os.path.join('modules', name), name)

        self.callback()

    def remove_module(self, btn):
        """
        Handler for removing module from list and filesystem
        """

        #Get current module name
        module = self.model.get(self.combo.get_active_iter(), 0)[0]

        #Display confirmation dialog
        dialog = gtk.MessageDialog(None,
                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                    gtk.MESSAGE_QUESTION,
                    gtk.BUTTONS_OK_CANCEL,
                    "Are you sure to delete module <b>{0}</b>?".format(module))
        response = dialog.run()
        dialog.destroy()


        if response == gtk.RESPONSE_CANCEL:
            return

        #Actually remove module
        self.model.remove(self.combo.get_active_iter())
        self.editor.flush_buffer(module)
        self.editor.remove_buffer(module)
        os.remove(os.path.join('modules', module))

        #Move selection to first module
        self.combo.set_active_iter(self.model.get_iter_first())

        #Update modules in main window
        self.callback()

    def input_dialog(self):
        """
        Function for creating and running simple input dialog

        Returns: inputed string
        """

        dialog = gtk.Dialog("Enter module name",
                            None,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                            gtk.STOCK_OK, gtk.RESPONSE_OK))
        #Populate dialog with widgets
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label("Enter new module name (with .json extension:"), False)
        entry = gtk.Entry()
        hbox.pack_start(entry)
        hbox.show_all()

        dialog.vbox.pack_start(hbox)

        response = dialog.run()
        if response == gtk.RESPONSE_CANCEL:
            text =  ''
        elif response == gtk.RESPONSE_OK:
            text = entry.get_text()

        dialog.destroy()
        return text

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
