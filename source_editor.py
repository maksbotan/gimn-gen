
import os
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
        self.current_buffer = 'empty'

        #Initialize source language for SourceView
        self.get_sourcelanguage()
        #Initialize SourceView widget and add to container
        self.view = gtksourceview2.View()
        #Customize it's appearence
        self.view.set_show_line_numbers(True)
        self.view.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        self.text_area.add(self.view)

        #Connect our signals
        widgets_tree.signal_autoconnect({
                    'save': self.save_buffer,
                    'undo': self.undo_action,
                    'redo': self.redo_action})

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

        #Store in form [buffer, filename]
        self.buffers[name] = [buffer, '']

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

        #Do switch and remember selection
        self.view.set_buffer(self.buffers[name][0])
        self.current_buffer = name

    def load_file_to_buffer(self, file_name, buffer_name):
        """
        Clean buffer and load file contents to it

        params:
            - file_name: Name of file to load from,
                should be text file in UTF-8
            - buffer_name: Name of buffer to load to, should be
                valid buffer created by allocate_buffer()
        """

        if not buffer_name in self.buffers or buffer_name == 'empty':
            #Invalid buffer, abort
            return

        if not os.path.exists(file_name):
            #If file doesn't exists, create new one
            open(file_name, 'w').write('')

        self.buffers[buffer_name][0].begin_not_undoable_action()
        self.buffers[buffer_name][0].set_text(open(file_name, 'r').read())
        self.buffers[buffer_name][0].end_not_undoable_action()
        self.buffers[buffer_name][1] = file_name

    def flush_buffer(self, buffer_name=None):
        """
        Save buffer to file on disk

        params:
            - buffer_name: Name of buffer to save. If None, use currently active one
        """

        if not buffer_name:
            #Use current buffer if none specified
            buffer_name = self.current_buffer

        if not buffer_name in self.buffers or buffer_name == 'empty':
            #Invalid buffer, abort
            return

        with open(self.buffers[buffer_name][1], 'w') as f:
            #Get gtk.TextIter pointing on start and end of buffer
            start, end = self.buffers[buffer_name][0].get_bounds()
            #Write buffer contents to file in UTF8
            f.write(self.buffers[buffer_name][0].get_text(start, end).encode('utf-8'))

    def save_buffer(self, btn):
        """
        Signal handler to save buffer on user request
        """

        self.flush_buffer()

    def undo_action(self, btn):
        """
        Signal handler to undo last action
        """

        if not self.current_buffer in self.buffers:
            #Invalid current buffer, abort
            return

        self.buffers[self.current_buffer][0].undo()

    def redo_action(self, btn):
        """
        Signal handler to redo last action
        """

        if not self.current_buffer in self.buffers:
            #Invalid current buffer, abort
            return

        self.buffers[self.current_buffer][0].redo()

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
