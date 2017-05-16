# The MIT License (MIT)
# Copyright (c) 2014-2017 University of Bristol
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.
from jinja2 import Undefined
import itertools


def custom_sort(iterable):
    if iterable is None or isinstance(iterable, Undefined):
        return iterable

    # Do custom sorting of iterable here
    iterable = sorted(iterable, key=lambda x: len(x.split(".")), reverse=False)
    return iterable


def custom_format(value, template):
    if isinstance(value, (list, tuple)):
        return ''.join(map(lambda x: template.format(x), value))
    return template.format(value)


def custom_format_old(value):
    header = '<table class="table table-bordered table-responsive"><tr>'
    template = '<td class="col-md-1">{}</td>'
    footer = '</tr></table>'

    if isinstance(value, (list, tuple)):
        content = ''.join(map(lambda x: template.format(x), value))
    else:
        content = template.format(value)

    return header + content + footer


def treelib_to_treeview(d):
    root = []

    def transform(node, link=''):
        nodes = []
        for item in node:
            if not link:
                link = '/view?'
            else:
                link += '&'
            text = "{}={}".format(item, node[item]['data'])
            link += text
            dd = dict(text=text, href=link)
            if 'children' in node[item]:
                # dd['nodes'] = [dict(text='x', nodes=transform(child)) for child in node[item]['children']]
                dd['nodes'] = list(itertools.chain(*[transform(child, link) for child in node[item]['children']]))
            nodes.append(dd)
        return nodes

    for v in d['root']['children']:
        root.append(dict(text="root", nodes=transform(v)))

    return root
