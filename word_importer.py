#!/usr/bin/end python

import os, subprocess, tempfile, shutil, mmap
from BeautifulSoup import BeautifulSoup

class WordImporter():
    """
    Class implementing generic word file to html converter.
    Uses 'wv' toolkit, http://wvware.sourceforge.net
    """

    def __init__(self, filename, image_path, image_dest):
        """
        Constructor

        params:
            - filename: Name of word file to import from
            - image_path: Path to images directory (from html point of view)
            - image_dest: Directory to move images to (in real filesystem)
        """

        if not os.path.exists(filename):
            raise ValueError('Not existing file given: %s' % filename)

        self.file = filename
        self.image_path = image_path
        self.image_dest = image_dest

    def __del__(self):
        """
        Destructor to ensure temp files are closed and removed from fs
        """
        
        try:
            self.html_map.close()
            self.html.close()
        except AttributeError:
            return

        os.remove(self.html.name)

    def get_content(self):
        """
        Load only real content of doc, doing image fixing
        """

        self._load(True)
        return self.html.name

    def get_full(self):
        """
        Load whole html page of doc, doing image fixing
        """

        self._load(False)
        return self.html.name

    def _fix_images(self):
        """
            Fix paths to images in html
        """

        #Parse html to BeautifulSoup object
        self.html_map.seek(0)
        bs = BeautifulSoup(self.html_map.read(len(self.html_map)))

        #Path to directory where images are stored by wvHtml
        img_dir = os.path.dirname(self.html.name)

        for image in bs('img'):
            file_name = image['src']

            #Put image to proper location
            shutil.move(os.path.join(img_dir, file_name), os.path.join(self.image_dest))
            #And change img src to proper path
            image['src'] = '{0}/{1}'.format(self.image_path, file_name)

        #Save fixed html in file
        html = bs.prettify()
        self.html_map.seek(0)
        self.html_map.resize(len(html))
        self.html_map.write(html)
        self.html_map.flush()

    def _load(self, do_crop=False):
        """
        Convert word file to html and store it in tempfile

        params:
            - do_crop: Whether to crop file to content or leave whole html
        """

        #Get temporary file where wvHtml will store output
        out_file = tempfile.mkstemp()[1]

        #Call wvHtml
        subprocess.check_call(['wvHtml', self.file, out_file])

        if do_crop:
            #Create mmap object for file
            self.html = open(out_file, 'r+b')
            self.html_map = mmap.mmap(self.html.fileno(), 0)
            #Get index of real data section start and end
            #21 is length of header
            start = self.html_map.find('<!--Section Begins-->') + 21
            end = self.html_map.rfind('<!--Section Ends-->')
            #Resize map to new size
            self.html_map.move(0, start, end - start)
            self.html_map.resize(end - start)
        else:
            #Just load output
            self.html = open(out_file, 'r+b')
            self.html_map = mmap.mmap(self.html.fileno(), 0)

        #Fix paths to images
        self._fix_images()
