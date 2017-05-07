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

from flask import Flask, render_template
from flask_bower import Bower
from hyperstream import HyperStream
import itertools


hs = HyperStream()
# a = 1


def treelib_to_treeview(d):
    root = []

    def transform(node):
        nodes = []
        for item in node:
            dd = dict(text="{}={}".format(item, node[item]['data']))
            if 'children' in node[item]:
                # dd['nodes'] = [dict(text='x', nodes=transform(child)) for child in node[item]['children']]
                dd['nodes'] = list(itertools.chain(*[transform(child) for child in node[item]['children']]))
            nodes.append(dd)
        return nodes

    for v in d['root']['children']:
        root.append(dict(text="root", nodes=transform(v)))

    return root

    # if isinstance(d, collections.Mapping):
    #     # return [{'text': k, 'nodes': [treelib_to_treeview(v['children'])]} for k, v in d.iteritems()]
    #     return [{'text': k, 'nodes': [treelib_to_treeview(x) for x in v['children']] if 'children' in v else v['data']} for k, v in d.iteritems()]
    # return d


app = Flask(__name__)
Bower(app)
app.jinja_env.add_extension('jinja2.ext.do')
app.jinja_env.filters['treelib_to_treeview'] = treelib_to_treeview


@app.route("/")
def index():
    return render_template("index.html", hyperstream=hs)


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host="0.0.0.0", port=5000, debug=True)
