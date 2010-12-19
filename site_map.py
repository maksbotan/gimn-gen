#!/usr/bin/env python
# -*- coding: utf8; -*-

structure = [
    { 'name': 'index',
      'title': 'Главная',
      'template': 'index.tmp',
      'modules': [ 'featured', 'notd'],
      'sources': [ 'index.cont' ],
      'subs': []
    },
    { 'name': 'innovacii',
      'title': 'Инновации',
      'template': 'main.tmp',
      'modules': [],
      'sources': 'innovacii.cont',
      'subs': [
                { 'name': 'introdaction',
                  'title': '«Введение в интеллектуальную жизнь»',
                  'template': 'main.tmp',
                  'modules': [],
                  'sources': 'introdaction.cont',
                  'subs': []
                },
              ]
     },
]
