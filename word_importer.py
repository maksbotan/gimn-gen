#!/usr/bin/end python

import beautifulsoup, subprocess, tempfile

class WordImporter():
    """
    Class implementing generic word file to html converter.
    Uses 'wv' toolkit, http://wvware.sourceforge.net
    """

    def __init__(self, filename):
        """
        Constructor

        params:
            - filename: Name of word file to import from
        """

        if not os.exists(filename):
            raise ValueError('Not existing file given: %s' % filename)

        self.file = filename

    def __del__(self):
        """
        Destructor to ensure temp files are closed and removed from fs
        """
        
        self.html_map.close()
        self.html.close()
        os.remove(self.html.name)

    def get_content(self):
        pass

    def get_full(self):
        pass

    def _load(self, do_crop=False):
        """
        Convert word file to html and store it in tempfile

        params:
            - do_crop: Whether to crop file to content or leave whole html
        """

        #Get temporary file where wvHtml will store output
        out_file = tempfile.mkstemp()

        #Call wvHtml
        subprocess.check_call(['wvHtml', self.filename, out_file])

        if do_crop:
            #Create mmap object for file
            self.html = open(out_file, 'r+b')
            self.html_map = mmap.mmap(self.html.fileno())
            #Get index of real data section start and end
            #21 is length of header
            start = self.html_map.find('<!--Section Begins-->') + 21
            end = self.html_map.rfind('<!--Section Ends-->')
            #Resize map to new size
            self.html_map.move(0, start, end-start)
            self.html_map.resize(end-start)

