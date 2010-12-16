#!/usr/bin/env python
# -*- coding: utf-8; -*-

nodes = [
    { 
        'link': 'index.html',
        'text': u'Главная',
        'subs': None
    },
    {
        'link': 'vizitka.htm',
        'text': u'Визитка',
        'subs': [
                    { 'link': 'vizitka/administration.htm',
                      'text': u'Администрация'
                    },
                    { 'link': 'vizitka/contacts.htm',
                      'text': u'Контактная информация'
                    }
                 ]
    },
]
