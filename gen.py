#!/usr/bin/env python

import jinja2

from modules import nav

env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

main_template = env.get_template('main.html')

print main_template.render(content="cont.html", nodes=nav.nodes).encode('utf8')
