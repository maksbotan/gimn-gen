#!/usr/bin/env python

import gtk, webkit
from os import getcwd

class WebkitWindow():
    """
    Class representing frame with webkit-based previewer and editor
    """

    def __init__(self):
        """
        Constructor

        params:
            - filename: Name of file to show
        """

        self.filename = ''
        self.title = ''
        self.visible = False

        #Construct main window from ui file
        self.widgets = gtk.Builder()
        self.widgets.add_from_file('webkit_window.ui')

        self.main_window = self.widgets.get_object('webkit_window')

        #Initialize webkit object and show it
        self.webkit = webkit.WebView()
        self.widgets.get_object('webkit_w').add(self.webkit)

        #Connect our signals
        self.widgets.connect_signals({'refresh': self.refresh})

    def load_file(self, filename, path, title=''):
        """
        Load html file to webkit

        params:
            - filename: Name of file to load from
            - path: Path to page relative to site root
            - title: Title of the page
        """

        if self.visible:
            #Load string 'cause webkit cannot load non-strict html's from files
            cwd = getcwd()
            html = '<link rel="stylesheet" href="{}/generated/style.css" type="text/css"\n<div class="wrapper1"><div class="wrapper"><div class="content">{}</div></div></div>'.format(cwd, open(filename).read().decode('utf-8'))
            self.webkit.load_string(html,
                                        'text/html',
                                        'utf-8',
                                        'file://{}/generated/{}/'.format(cwd, path))

            self.filename = filename
            if title:
                self.title = title
                self.main_window.set_title('{0} - Preview'.format(title))
            else:
                self.main_window.set_title('Preview')

    def refresh(self, btn=None):
        """
        Refresh file in webkit
        """

        if self.visible and self.filename:
            self.load_file(self.filename, self.title)

    def show(self):
        """
        Show window
        """

        self.main_window.show_all()
        self.visible = True

    def hide(self):
        """
        Hide window
        """

        self.main_window.hide_all()
        self.visible = False

if __name__ == '__main__':
    wk = WebkitWindow()
    wk.show()
    wk.main_window.connect('destroy', gtk.main_quit)
    wk.load_file('content/nii.cont')
    gtk.main()
