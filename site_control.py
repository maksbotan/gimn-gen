
import os
import gtk, gobject

class SiteControl():
    """
    Class to represent site controlling widgets
    """

    def __init__(self, widgets_tree):
        """
        Constructor

        params:
            - widgets_tree: gtk.glade.XML object
        """
        
        #Get content container and button VBox
        self.content = widgets_tree.get_widget('control')
        self.vbox = widgets_tree.get_widget('control_vbox')
        #Detach from useless gtk.Window
        widgets_tree.get_widget('control_window').remove(self.content)

    def get_content(self):
        """
        Return content widget for embedding in main window
        """

        return self.content
