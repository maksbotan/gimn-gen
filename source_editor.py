
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

    def get_content(self):
        """
        Return main widget for embedding in main window
        """

        return self.editor_vbox
