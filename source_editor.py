
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

        #Initialize source language for SourceView
        self.get_sourcelanguage()
        #Initialize SourceView widget and add to container
        self.view = gtksourceview2.View()
        #Enable line numbers in it
        self.view.set_show_line_numbers(True)
        self.text_area.add(self.view)

    def get_sourcelanguage(self):
        """
        Get gtksourceview2.Language instance for html
        """
        lm = gtksourceview2.LanguageManager()
        self.lang = lm.get_language('html')

    def get_content(self):
        """
        Return main widget for embedding in main window
        """

        return self.editor_vbox
