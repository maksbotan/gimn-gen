
import os, StringIO
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
        #Detach from useless gtk.Window
        widgets_tree.get_widget('control_window').remove(self.content)

        #Get and save space for showing generation results
        self.status_text = widgets_tree.get_widget('output_text')
        self.status_buffer = self.status_text.get_buffer()
        self.status_buffer.set_text('')

        widgets_tree.signal_connect('generate', self.generate)
    
    def generate(self, btn):
        """
        Start generator and show it's output in textview
        """
        import gen

        #Swap gen's sys.stdout with StringIO object to show it pn form
        buffer = StringIO.StringIO()
        gen.sys.stdout = buffer
        #Disable colored output
        gen.colors = {'normal':'', 'good':'', 'err':'', 'warn':''}

        generator = gen.Generator()
        self.status_buffer.set_text('')

        #Start regeneration
        generator.regen_site()
        
        #Display results
        self.status_buffer.set_text(buffer.getvalue())

        print 'THE END'

    def get_content(self):
        """
        Return content widget for embedding in main window
        """

        return self.content
