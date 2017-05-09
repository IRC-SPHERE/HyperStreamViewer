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

from flask import Flask, render_template, request
from flask_bower import Bower
from hyperstream import HyperStream, StreamId
from hyperstream.utils import MultipleStreamsFoundError, StreamNotFoundError, StreamNotAvailableError
from plotting import get_bokeh_plot

from bokeh.util.string import encode_utf8

from view_helpers import treelib_to_treeview, custom_sort


hs = HyperStream()
app = Flask(__name__)
Bower(app)
app.jinja_env.add_extension('jinja2.ext.do')
app.jinja_env.filters['treelib_to_treeview'] = treelib_to_treeview
app.jinja_env.filters['custom_sort'] = custom_sort


@app.route("/")
def index():
    return render_template("index.html", hyperstream=hs)


# @app.route("/dashboard")
# def dashboard():
#     return render_template("dashboard.html")

@app.route("/plates")
def plates():
    return render_template("plates.html", hyperstream=hs)


@app.route("/meta_data")
def meta_data():
    return render_template("meta_data.html", hyperstream=hs)


@app.route("/channels")
def channels():
    return render_template("channels.html", hyperstream=hs)


@app.route("/streams")
def streams():
    error = None
    try:
        d = dict(request.args.items())
        channel = d.pop("channel")
        stream = hs.channel_manager[channel].find_stream(**d)
    except (MultipleStreamsFoundError, StreamNotFoundError, StreamNotAvailableError, KeyError) as e:
        stream = None
        error = e

    return render_template("streams.html", hyperstream=hs, stream=stream, error=error)


@app.route("/view")
def view():
    streams = hs.channel_manager.mongo.find_streams(**dict(request.args.items()))
    # return render_template("view.html", streams=streams)
    x = list(range(0, 100))

    plot = get_bokeh_plot(title="Polynomial", x=x, y=list(map(lambda xx: xx ** 2, x)))

    html = render_template(
        'view.html',
        **plot
    )
    return encode_utf8(html)


@app.route("/polynomial")
def polynomial():
    """ Very simple embedding of a polynomial chart
    """
    # Create a polynomial line graph with those arguments
    x = list(range(0, 100))

    plot = get_bokeh_plot(title="Polynomial", x=x, y=list(map(lambda xx: xx ** 2, x)))

    html = render_template(
        'embed.html',
        **plot
    )
    return encode_utf8(html)


if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host="0.0.0.0", port=5000, debug=True)
