
import gtk, gobject, gtksourceview2

class SourceEditor():
    """
    Class representing source editor
    """

    def __init__(self, widgets_tree):
        """
        Constructor for SourceEditor class

        params:
            - widgets_tree: gtk.glade.XML object with needed widgets
        """

        #Get main widgets container
        self.editor_vbox = widgets_tree.get_widget('editor')
        #Detach it from useless gtk.Window
        wnd = widgets_tree.get_widget('editor_window')
        wnd.remove(self.editor_vbox)
        wnd.destroy()

        #Get gtk.ScrolledWindow, which is container for sourceview
        self.text_area = widgets_tree.get_widget('text_area')

        #Dict of TextBuffers for editor
        self.buffers = {}

        #Initialize source language for SourceView
        self.get_sourcelanguage()
        #Initialize SourceView widget and add to container
        self.view = gtksourceview2.View()
        #Enable line numbers in it
        self.view.set_show_line_numbers(True)
        self.text_area.add(self.view)

        #Create empty buffer and switch to it
        self.allocate_buffer('empty')
        self.switch_to_buffer('empty')

    def allocate_buffer(self, name):
        """
        Create a new gtk.SourceBuffer, set it's properties and store for future use

        params:
            - name: Name of buffer to create
        """

        if name in self.buffers:
            #Buffer already exists, abort
            return

        buffer = gtksourceview2.Buffer()
        buffer.set_language(self.lang)

        self.buffers[name] = buffer

    def remove_buffer(self, name):
        """
        Remove no more needed buffer

        params:
            - name: Name of buffer to remove
        """

        if not name in self.buffers:
            #No such buffer exists, abort
            return

        del self.buffers[name]

    def switch_to_buffer(self, name):
        """
        Change current buffer in SourceView to name

        params:
            - name: Name of buffer to switch to
        """

        if not name in self.buffers:
            #No such buffer exists, abort
            return

        #Do switch
        self.view.set_buffer(self.buffers[name])

    def get_sourcelanguage(self):
        """
        Get gtksourceview2.Language instance for html
        """
        self.lm = gtksourceview2.LanguageManager()
        self.lang = self.lm.get_language('html')

    def get_content(self):
        """
        Return main widget for embedding in main window
        """

        return self.editor_vbox
