
import os, shutil
import gtk, gobject, gtk.glade, gtksourceview2
from word_importer import WordImporter

class SourceEditor():
    """
    Class representing source editor
    """

    def __init__(self, language='html'):
        """
        Constructor for SourceEditor class

        params:
            - widgets_tree: gtk.glade.XML object with needed widgets
        """

        #Load glade widgets from file
        widgets_tree = gtk.glade.XML('source_editor.ui')

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
        self.get_sourcelanguage(language)
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
                    'redo': self.redo_action,
                    'word_import': self.word_import,
                    'embed_image': self.embed_image,
                    'embed_file': self.embed_file})

        #Create empty buffer and switch to it
        self.allocate_buffer('empty')
        self.switch_to_buffer('empty')

    def allocate_buffer(self, name, level=0, path=''):
        """
        Create a new gtk.SourceBuffer, set it's properties and store for future use

        params:
            - name: Name of buffer to create
            - level: Level of page in site directory structure
            - path: Path to page relative to site root
        """

        if name in self.buffers:
            #Buffer already exists, abort
            return

        buffer = gtksourceview2.Buffer()
        buffer.set_language(self.lang)

        #Store in form [buffer, filename, level]
        self.buffers[name] = [buffer, '', level, path]

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

    def word_import(self, btn):
        """
        Signal handler to allow user load word document into current buffer
        """

        if not self.current_buffer in self.buffers:
            #Wrong buffer, abort
            return

        buf = self.buffers[self.current_buffer]

        #Create gtk file dialog and set up filter in it
        file_filter = gtk.FileFilter()
        file_filter.set_name('MS Word document')
        file_filter.add_mime_type('application/msword')

        #Get file from user
        filename = self.open_file_dialog("Choose your word document", file_filter)
        if not filename:
            return

        #Initialize word importer
        importer = WordImporter(filename, '{0}images'.format('../'*buf[2]),
                                'generated/images')
        result = importer.get_content()

        #Place file to proper location
        shutil.copy(result, buf[1])

        #Update contents in buffer
        self.load_file_to_buffer(buf[1], self.current_buffer)

    def embed_image(self, btn):
        """
        Signal handler to copy image to site and paste correct <img> tag to buffer
        """

        if not self.current_buffer in self.buffers:
            #Wrong buffer, abort
            return

        buf = self.buffers[self.current_buffer]

        #Create gtk file dialog and set up filter in it
        file_filter = gtk.FileFilter()
        file_filter.set_name('Image file')
        file_filter.add_mime_type('image/*')

        #Get file from user
        filename = self.open_file_dialog("Choose image file", file_filter)
        if not filename:
            return

        #Copy image file to proper location
        shutil.copy(filename, 'generated/images')

        #Build <img> tag
        tag = '<img alt="{1}" src="{0}images/{1}"'.format('../'*buf[2],
                            os.path.basename(filename))

        #Insert img tag to page
        buf[0].insert_at_cursor(tag)

    def embed_file(self, btn):
        """
        Signal handler to copy and paste link to generic file
        """

        if not self.current_buffer in self.buffers:
            #Wrong buffer, abort
            return

        buf = self.buffers[self.current_buffer]

        #Get file from user
        filename = self.open_file_dialog()
        if not filename:
            return

        #Copy image file to proper location
        shutil.copy(filename, 'generated/files')

        #Build <a> tag
        tag = '<a href="{0}files/{1}"> </a>'.format('../'*buf[2], 
                            os.path.basename(filename))

        #Insert 'a' tag to page
        buf[0].insert_at_cursor(tag)

    def open_file_dialog(self, title="Choose file", f_filter=None):
        """
        Auxillary function to construct and run gtk file dialog
        params
            - title: Title to display on dialog
            - f_filter: gtk.FileFilter object for dialog
        """

        dialog = gtk.FileChooserDialog(title,
                             action=gtk.FILE_CHOOSER_ACTION_OPEN,
                             buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                      gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        if f_filter:
            dialog.add_filter(f_filter)

        res = dialog.run()

        if res == gtk.RESPONSE_OK:
            filename = dialog.get_filename()
        else:
            filename = ''

        dialog.destroy()
        return filename

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

    def get_sourcelanguage(self, language):
        """
        Get gtksourceview2.Language instance for required lang
        """
        self.lm = gtksourceview2.LanguageManager()
        self.lang = self.lm.get_language(language)

    def get_content(self):
        """
        Return main widget for embedding in main window
        """

        return self.editor_vbox
